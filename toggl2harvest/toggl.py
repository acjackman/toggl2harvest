# Standard Library
import logging
import time

# Third Party Packages
import requests
from boltons.cacheutils import cachedproperty
from requests.exceptions import HTTPError
from ruamel.yaml import YAML

from toggl2harvest.utils import iso_date, iso_timestamp


log = logging.getLogger(__name__)

TIME_API = 'https://www.toggl.com/api/v8'
REPORTS_API = 'https://toggl.com/reports/api/v2'


class InvalidCredentialsError(Exception):
    pass


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
        first_call = True
        try:
            while True:
                r = self.session.get(url, params=params)
                r.raise_for_status()
                time_entries_r = r.json()
                time_entries = time_entries + time_entries_r['data']

                first_call = False  # Made the first api call

                if len(time_entries) >= time_entries_r['total_count']:
                    break
                else:
                    params['page'] += 1
                    if not first_call:
                        time.sleep(1)
        except HTTPError as e:
            if e.response.status_code == 401:
                raise InvalidCredentialsError()
            raise
        return time_entries

    def toggl_download_params(self, cred_file):
        try:
            with YAML() as yaml:
                creds = yaml.load(cred_file)
        except TypeError:
            return {}

        try:
            creds_toggl = creds['toggl']
            params = creds_toggl['dowload_data_params']
        except KeyError:
            return {}

        if not isinstance(params, dict) :
            return {}

        return params
