import logging
from os import path

import requests
from yaml import load as load_yaml, dump as dump_yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

log = logging.getLogger(__name__)

HARVEST_API = 'https://api.harvestapp.com/api/v2'


class HarvestCredentials():

    def __init__(self, account_id, token, user_agent):
        self.account_id = account_id
        self.token = token
        self.user_agent = user_agent

    @classmethod
    def read_from_file(cls, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            credentials_dict = load_yaml(f, Loader=Loader)

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

    def _cache_file(self, working_dir):
        return path.join(working_dir, 'harvest_cache.yml')

    def clear_project_cache(self, working_dir):
        with open(self._cache_file(working_dir), 'w') as f:
            f.write('')

    def read_project_cache(self, working_dir):
        with open(self._cache_file(working_dir), 'r') as f:
            return load_yaml(f, Loader=Loader)

    def write_project_cache(self, harvest_projects, working_dir):
        with open(self._cache_file(working_dir), 'r') as f:
            f.write(dump_yaml(
                harvest_projects,
                Dumper=Dumper,
                default_flow_style=False
            ))

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
