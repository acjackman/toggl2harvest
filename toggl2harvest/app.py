# Standard Library
import logging
import os
from collections import namedtuple
from datetime import datetime
from os.path import expanduser
from pathlib import Path

# Third Party Packages
from boltons.cacheutils import cachedproperty
from marshmallow.exceptions import ValidationError as MarshmallowValidationError
from requests.exceptions import HTTPError
from ruamel.yaml import YAML

from . import harvest, schemas, toggl
from .exceptions import (
    IncompleteHarvestData,
    InvalidFileError,
    InvalidHarvestProject,
    InvalidHarvestTask,
    MissingHarvestProject,
    MissingHarvestTask,
)
from .models import HarvestCache, HarvestEntry, ProjectMapping
from .utils import AtomicFileUpdate, iso_timestamp


log = logging.getLogger(__name__)


TimeEntryWriteResult = namedtuple(
    'TimeEntryWriteResult',
    ' '.join([
        'day',
        'written',
    ])
)


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
    def _harvest_cache_file(self):
        return Path(os.path.join(self.config_dir, 'harvest_cache.yml'))

    @cachedproperty
    def harvest_cache(self):
        schema = schemas.HarvestCacheEntrySchema()
        harvest_projects = []
        with YAML() as yaml:
            for i, entry in enumerate(yaml.load_all(self._harvest_cache_file)):
                harvest_projects.append(schema.load(entry))
        return HarvestCache(harvest_projects)

    @cachedproperty
    def project_file(self):
        return Path(os.path.join(self.config_dir, 'project_mapping.yml'))

    @cachedproperty
    def project_mapping(self):
        with YAML() as yaml:
            return ProjectMapping(yaml.load(self.project_file))

    @cachedproperty
    def time_log_schema(self):
        return schemas.TimeLogSchema()

    def cache_harvest_projects(self):
        harvest_projects = self.harvest_api.cache_projects_via_api()
        yaml = YAML()
        yaml.dump_all(harvest_projects, self._harvest_cache_file)

    def download_toggl_data(self, start, end):
        toggl_time_entries = self.toggl_api.retrieve_time_entries(
            start,
            end,
            params=self.toggl_api.toggl_download_params(self.cred_file)
        )
        return self.toggl_api.create_time_entries(toggl_time_entries)

    def write_time_entries(self, time_entries):
        schema = schemas.TimeLogSchema()
        for day, day_entries in time_entries.items():
            day_file = Path(self.data_dir, f'{day:%Y-%m-%d}.yml')
            # TODO: Check that date hasn't been opened before
            if day_file.exists():
                yield TimeEntryWriteResult(day=day, written=False)
                continue  # Don't overwrite existing data

            with YAML(output=day_file) as yaml:
                for entry in day_entries:
                    yaml.dump(schema.dump(entry))

            yield TimeEntryWriteResult(day=day, written=True)

    def validate_file(self, day_file):
        file_errors = 0

        if not day_file.is_file():
            return file_errors

        with AtomicFileUpdate(day_file) as file, YAML(output=file.output) as yaml:
            try:
                for i, data in enumerate(yaml.load_all(file.input)):
                    time_log = self.time_log_schema.load(data)
                    updated_data, valid, = self._update_entry(i, data, time_log)
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

    def upload_to_harvest(self, day):
        day_file = self.data_file(day)

        if not day_file.is_file():
            return []

        results = []
        with AtomicFileUpdate(day_file) as file, YAML(output=file.output) as yaml:
            try:
                for i, data in enumerate(yaml.load_all(file.input)):
                    time_log = self.time_log_schema.load(data)
                    data, valid, = self._update_entry(i, data, time_log)
                    if valid:
                        data, message = self._upload_entry_to_harvest(day, data, time_log)
                        results.append(message)
                    else:
                        results.append('Entry invalid, skipping')
                    yaml.dump(data)
                file.commit()
            except MarshmallowValidationError:
                raise InvalidFileError(f'{i:02d} entry is not parseable, skipping this file')

        return results

    def _upload_entry_to_harvest(self, day, data, time_log):
        if not time_log.is_billable:
            return data, 'Not billable, skipping.'

        if time_log.harvest.uploaded is not None:
            return data, 'Already uploaded, skipping.'

        entry = HarvestEntry.from_time_log(day, time_log)
        try:
            self.harvest_api.create_time_entry(entry)
            data['harvest']['uploaded'] = iso_timestamp(datetime.now())
        except HTTPError:
            return data, 'Error uploading to Harvest, skipping.'

        return data, 'Uploaded'
