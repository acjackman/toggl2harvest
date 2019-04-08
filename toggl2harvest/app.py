# Standard Library
import io
import logging
import os
from os.path import expanduser
from pathlib import Path

# Third Party Packages
from boltons.cacheutils import cachedproperty
import click
from ruamel.yaml import YAML
from marshmallow.exceptions import ValidationError as MarshmallowValidationError

from . import harvest, schemas, toggl
from .exceptions import (
    IncompleteHarvestData,
    MissingHarvestProject,
    MissingHarvestTask,
    InvalidHarvestTask,
    InvalidHarvestProject,
)
from .utils import AtomicFileUpdate


log = logging.getLogger(__name__)


class TogglHarvestApp(object):

    def __init__(self, config_dir=None):
        self.config_dir = expanduser(config_dir or '.')

    @cachedproperty
    def cred_file(self):
        """Path to the credentialas file for this application."""
        return Path(self.config_dir, 'credentials.yaml')

    @cachedproperty
    def data_dir(self):
        """Path to the credentialas file for this application."""
        return Path(self.config_dir, 'data')

    def data_file(self, file_name):
        """Data file for this application."""
        return Path(self.data_dir, file_name + '.yml')

    @cachedproperty
    def toggl_cred(self):
        return toggl.TogglCredentials.read_from_file(self.cred_file)

    @cachedproperty
    def toggl_api(self):
        return toggl.TogglSession(self.toggl_cred)

    @cachedproperty
    def harvest_cred(self):
        return harvest.HarvestCredentials.read_from_file(self.cred_file)

    @cachedproperty
    def harvest_api(self):
        return harvest.HarvestSession(self.harvest_cred)

    @cachedproperty
    def project_file(self):
        return Path(os.path.join(self.config_dir, 'project_mapping.yml'))

    @cachedproperty
    def project_mapping(self):
        with YAML() as yaml:
            return yaml.load(self.project_file)

    @cachedproperty
    def time_log_schema(self):
        return schemas.TimeLogSchema()

    def cache_harvest_projects(self):
        self.harvest_api.update_project_cache(self.config_dir)

    def download_toggl_data(self, start, end):
        toggl_time_entries = self.toggl_api.retrieve_time_entries(
            start,
            end,
            params=self.toggl_api.toggl_download_params(self.cred_file)
        )
        self.toggl_api.write_report_data(toggl_time_entries, self.data_dir)

    def validate_file(self, day_file):
        file_errors = 0

        if not day_file.is_file():
            return file_errors

        with AtomicFileUpdate(day_file) as file, YAML(output=file.output) as yaml:
            try:
                for i, data in enumerate(yaml.load_all(file.input)):
                    time_log = self.time_log_schema.load(data)
                    updated_data, valid, = self._update_entry(i, data, time_log)
                    log.debug(valid)
                    file_errors += not valid
                    yaml.dump(updated_data)
                file.commit()
            except MarshmallowValidationError:
                file_errors += 1
                pass  # Atomic File Update will rollback any changes to the file

        return file_errors

    def _update_entry(self, i, data, time_log):
        valid = True
        try:
            time_log.update_harvest_tasks(
                self.project_mapping, self.harvest_cache)
            data['harvest']['project_id'] = time_log.harvest.project_id
            data['harvest']['task_id'] = time_log.harvest.task_id
        except IncompleteHarvestData as e:
            if isinstance(e, MissingHarvestProject):
                log.debug(f'Harvest Project missing for entry {i}')
            elif isinstance(e, MissingHarvestTask):
                log.debug(f'Harvest Task missing for entry {i}')
            elif isinstance(e, InvalidHarvestTask):
                log.debug(f'Harvest Task invalid for entry {i}')
            elif isinstance(e, InvalidHarvestProject):
                log.debug(f'Harvest Project invalid for entry {i}')
            valid = False

        return data, valid
