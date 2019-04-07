# Standard Library
import logging
import os
from os.path import expanduser
from pathlib import Path

# Third Party Packages
import click
from boltons.cacheutils import cachedproperty
from ruamel.yaml import YAML

from . import harvest, toggl


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

    def data_file_path(self, date_str):
        """Path to a data file for this application."""
        return Path(self.config_dir, 'data', f'{date_str}.yml')

    def data_file(self, file_path, atomic=True):
        """Data file for this application."""
        return click.open_file(self.config_dir, file_path, atomic=atomic)

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

    def cache_harvest_projects(self):
        self.harvest_api.update_project_cache(self.config_dir)

    def download_toggl_data(self, start, end):
        toggl_time_entries = self.toggl_api.retrieve_time_entries(
            start,
            end,
            params=self.toggl_api.toggl_download_params(self.cred_file)
        )
        self.toggl_api.write_report_data(toggl_time_entries, self.data_dir)
