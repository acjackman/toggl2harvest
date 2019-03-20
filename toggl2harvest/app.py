import logging
from os.path import expanduser
from datetime import datetime, timedelta
from pathlib import Path

# Third Party Packages
import click
from dateutil import parser as dateutil_parser
from ruamel.yaml import YAML
from boltons.cacheutils import cachedproperty

from toggl2harvest import toggl, harvest
from toggl2harvest.utils import strp_iso8601

log = logging.getLogger(__name__)


class TogglHarvestApp(object):

    def __init__(self, config_dir=None):
        self.config_dir = expanduser(config_dir or '.')

    @cachedproperty
    def cred_file(self):
        """Path to the credentialas file for this application."""
        return Path(self.config_dir, 'credentials.yaml')

    def data_file_path(self, date_str):
        """Path to a data file for this application."""
        return Path(self.config_dir, 'data', f'{date_str}.yml')

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

    def cache_harvest_projects(self):
        self.harvest_api.update_project_cache(self.config_dir)
