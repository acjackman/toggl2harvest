# Standard Library
import logging
from os import path
from pathlib import Path

# Third Party Packages
import requests
from ruamel.yaml import YAML


log = logging.getLogger(__name__)

HARVEST_API = 'https://api.harvestapp.com/api/v2'


class HarvestCredentials():

    def __init__(self, account_id, token, user_agent):
        self.account_id = account_id
        self.token = token
        self.user_agent = user_agent

    @classmethod
    def read_from_file(cls, file_path):
        with YAML() as yaml:
            credentials_dict = yaml.load(file_path)

        if not isinstance(credentials_dict, dict):
            raise TypeError('credentials should be a dict.')

        harvest_cred = credentials_dict['harvest']

        account_id = harvest_cred['account_id']
        token = harvest_cred['token']
        user_agent = harvest_cred['user_agent']
        return HarvestCredentials(account_id, token, user_agent)


class HarvestSession():

    def __init__(self, credentials, session=requests.Session()):
        self.session = session
        self.session.headers = {
            'Harvest-Account-ID': credentials.account_id,
            'Authorization': f'Bearer {credentials.token}',
            'User-Agent': credentials.user_agent,
        }

    @classmethod
    def _cache_file(cls, working_dir):
        return Path(path.join(working_dir, 'harvest_cache.yml'))

    def clear_project_cache(self, working_dir):
        with open(self._cache_file(working_dir), 'w') as f:
            f.write('')

    @classmethod
    def read_project_cache(cls, working_dir):
        with YAML() as yaml:
            return yaml.load(cls._cache_file(working_dir))

    def write_project_cache(self, harvest_projects, working_dir):
        with YAML(output=self._cache_file(working_dir)) as yaml:
            yaml.dump(harvest_projects)

    def update_project_cache(self, working_dir):
        harvest_projects = self.read_project_cache()
        self.identify_projects_from_timeline(
            harvest_projects=harvest_projects
        )
        self.write_project_cache(harvest_projects)
        return harvest_projects

    def identify_projects_from_timeline(self, harvest_projects={}):
        time_entries = self.retrieve_time_entries()

        for te in time_entries:
            project_id = te['project']['id']
            try:
                project = harvest_projects[project_id]
            except KeyError:
                harvest_projects[project_id] = {
                    'tasks': {},
                    'name': te['project']['name']
                }
                project = harvest_projects[project_id]

            task_id = te['task']['id']
            project['tasks'][task_id] = te['task']['name']

        return harvest_projects

    def retrieve_time_entries(self):
        time_entries = []
        next_url = f'{HARVEST_API}/time_entries'
        while next_url is not None:
            r = self.session.get(next_url)
            r.raise_for_status()
            time_entries_r = r.json()
            time_entries = time_entries + time_entries_r['time_entries']
            next_url = time_entries_r['links']['next']
        return time_entries

    def create_time_entry(self, entry):
        r = self.session.post(
            f'{HARVEST_API}/time_entries',
            json={
                'project_id': entry.project_id,
                'task_id': entry.task_id,
                'spent_date': entry.spent_date,
                'hours': entry.hours,
                'notes': entry.notes,
            }
        )
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            log.info(r.request.body)
            raise
        return r.json()
