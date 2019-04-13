# Standard Library
import logging

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

    def cache_projects_via_api(self):
        projects = self.retrieve_projects()
        task_assignments = self.retrieve_task_assignments()

        harvest_cache = {}
        for project in projects:
            p_id = project['id']
            c_id = project['client']['id']
            harvest_cache[p_id] = {
                'id': p_id,
                'name': project['name'],
                'active': project['is_active'],
                'client': {
                    'id': c_id,
                    'name': project['client']['name']
                },
                'code': project['code'],
                'tasks': {},
            }

        for task in task_assignments:
            project_tasks = harvest_cache[task['project']['id']]['tasks']
            task_id = task['task']['id']
            project_tasks[task_id] = {
                'name': task['task']['name'],
                'link_active': task['is_active'],
            }

        cache_array = sorted(
            harvest_cache.values(),
            key=lambda e: (not e['active'], e['name']))
        return cache_array

    def retrieve_projects(self):
        return self._retrieve_list('projects')

    def retrieve_task_assignments(self):
        return self._retrieve_list('task_assignments')

    def _retrieve_list(self, list_name):
        objects = []
        next_url = f'{HARVEST_API}/{list_name}'
        while next_url is not None:
            r = self.session.get(next_url)
            r.raise_for_status()
            r_json = r.json()
            objects = objects + r_json[list_name]
            next_url = r_json['links']['next']
        return objects

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
