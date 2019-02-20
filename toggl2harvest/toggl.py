import logging
from time import sleep

import requests
from yaml import load as load_yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader
from ruamel.yaml import YAML


log = logging.getLogger(__name__)

TIME_API = 'https://www.toggl.com/api/v8'
REPORTS_API = 'https://toggl.com/reports/api/v2'


def iso_date(time_value):
    return time_value.strftime('%Y-%m-%d')


def iso_timestamp(time_value):
    return time_value.strftime('%Y-%m-%dT%H:%M:%S%z')


class TogglCredentials():

    def __init__(self, api_token, workspace_id, user_agent):
        self.api_token = api_token
        self.workspace_id = workspace_id
        self.user_agent = user_agent

    @classmethod
    def read_from_file(cls, file_path):
        with YAML() as yaml:
            credentials_dict = yaml.load(file_path)

        if not isinstance(credentials_dict, dict):
            raise TypeError('credentials should be a dict.')

        toggl_cred = credentials_dict['toggl']

        api_token = toggl_cred['api_token']
        workspace_id = toggl_cred['workspace_id']
        user_agent = toggl_cred['user_agent']
        return TogglCredentials(api_token, workspace_id, user_agent)

    @property
    def auth(self):
        return (self.api_token, 'api_token')


class TogglSession():
    def __init__(self, credentials, session=requests.Session()):
        session.auth = credentials.auth
        self.session = session
        self.workspace_id = credentials.workspace_id
        self.user_agent = credentials.user_agent

    def retrieve_time_entries(self, start_date, end_date, params={}):
        url = f'{REPORTS_API}/details'
        params = {
            **params,
            'workspace_id': self.workspace_id,
            'since': iso_date(start_date),
            'until': iso_date(end_date),
            'user_agent': self.user_agent,
            'page': 1,
        }
        time_entries = []
        api_calls = 0
        while True:
            r = self.session.get(url, params=params)
            r.raise_for_status()
            time_entries_r = r.json()
            time_entries = time_entries + time_entries_r['data']

            api_calls += 1

            if len(time_entries) >= time_entries_r['total_count']:
                break
            else:
                params['page'] += 1
                if api_calls > 1:
                    sleep(1)

        return time_entries
