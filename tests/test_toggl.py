# Standard Library
from datetime import datetime as dt
from inspect import cleandoc
from pprint import pprint

# Third Party Packages
import pytest
from requests.exceptions import HTTPError

from toggl2harvest import toggl
from toggl2harvest.models import TimeLog


@pytest.fixture
def toggl_credentials():
    return toggl.TogglCredentials(
        api_token='123',
        workspace_id=123,
        user_agent='123',
    )


@pytest.fixture
def toggl_session(toggl_credentials):
    return toggl.TogglSession(toggl_credentials)


class TestDownloadParams:
    def test_toggl_download_params(self, toggl_session):
        params = toggl_session.toggl_download_params(cleandoc(
            """
            toggl:
              dowload_data_params:
                project_ids: '123'
            """
        ))

        assert params == {'project_ids': '123'}

    @pytest.mark.parametrize('file_contents', [
        # No Toggl key
        """
        bob_ross:
            dowload_data_params: 'abc'
        """,
        # No download params
        """
        toggl:
            api_token: 'abc'
        """,
        # Params not an object
        """
        toggl:
            dowload_data_params: 'abc'
        """,
        """
        toggl:
            dowload_data_params:
                - foo
                - bar
        """,
    ])
    def test_toggl_download_errors(self, toggl_session, file_contents):
        params = toggl_session.toggl_download_params(
            cleandoc(file_contents)
        )

        assert params == {}

    def test_toggl_download_params_file_not_exists(self, toggl_session, tmpdir):
        params = toggl_session.toggl_download_params(tmpdir.join('not_real.yml'))

        assert params == {}


class MockResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self.json_data = json_data
        self.checked_for_status = False

    def json(self):
        return self.json_data

    def raise_for_status(self):
        self.checked_for_status = True


class TestRetrieveTimeEntries:
    def test_valid_access(self, mocker, toggl_session):
        session_mock = mocker.patch.object(toggl_session, 'session', autospec=True)
        mocker.patch.object(
            session_mock, 'get',
            side_effect=[MockResponse(200, d) for d in [
                {
                    'total_count': 1,
                    'data': [{'toggl': 'response'}],
                },
            ]])

        time_entries = toggl_session.retrieve_time_entries(
            start_date=dt(2019, 1, 1),
            end_date=dt(2019, 1, 1),
        )

        assert session_mock.get.call_count == 1
        assert time_entries == [{'toggl': 'response'}]

    def test_pages_data(self, mocker, toggl_session):
        sleep_mock = mocker.patch('time.sleep')
        session_mock = mocker.patch.object(toggl_session, 'session', autospec=True)
        mocker.patch.object(
            session_mock, 'get',
            side_effect=[MockResponse(200, d) for d in [
                {
                    'total_count': 2,
                    'data': [{'toggl': 'response'}],
                },
                {
                    'total_count': 2,
                    'data': [{'toggl': 'response'}],
                },
            ]])

        time_entries = toggl_session.retrieve_time_entries(
            start_date=dt(2019, 1, 1),
            end_date=dt(2019, 1, 1),
        )

        assert session_mock.get.call_count == 2
        assert time_entries == [{'toggl': 'response'}, {'toggl': 'response'}]
        assert sleep_mock.call_count == 1

    def test_bad_password(self, mocker, toggl_session):
        session_mock = mocker.patch.object(toggl_session, 'session', autospec=True)
        mocker.patch.object(
            session_mock, 'get',
            side_effect=HTTPError(response=MockResponse(401, 'Unauthorized')))

        with pytest.raises(toggl.InvalidCredentialsError):
            toggl_session.retrieve_time_entries(
                start_date=dt(2019, 1, 1),
                end_date=dt(2019, 1, 1),
            )

        assert session_mock.get.call_count == 1


basic_data = {
    'pid': 123,
    'tid': 678,
    'description': 'Task Description',
    'start': '2019-01-01T12:00:00-07:00',
    'end': '2019-01-01T12:30:00-07:00',
    'client': 'Client Name',
    'project': 'Project Name',
    'task': 'Type of Work',
    'is_billable': True,
    'tags': [],
}


class TestCreateTimeEntries:
    def test_collapses_time_entries(self, toggl_session):
        report_data = [
            {**basic_data}, {
                **basic_data,
                'start': '2019-01-01T12:30:00-07:00',
                'end': '2019-01-01T13:00:00-07:00',
            }
        ]

        time_entries = toggl_session.create_time_entries(report_data)

        assert len(time_entries.keys()) == 1  # Only one day
        day_entries = list(time_entries.values())[0]
        pprint(day_entries)
        assert len(day_entries) == 1  # Only one TimeLog
        entry = day_entries[0]
        assert isinstance(entry, TimeLog)
        assert len(entry.time_entries) == 2

    @pytest.mark.parametrize('report_data', [
        [
            {**basic_data}, {
                **basic_data,
                'task': 'Different Type of Work',
            }
        ],
        [
            {**basic_data}, {
                **basic_data,
                'client': 'Different Client',
            }
        ],
        [
            {**basic_data}, {
                **basic_data,
                'project': 'Different Project',
            }
        ],
        [
            {**basic_data}, {
                **basic_data,
                'is_billable': False,
            }
        ],
    ])
    def test_does_not_collapses_time_entris(self, toggl_session, report_data):
        time_entries = toggl_session.create_time_entries(report_data)

        assert len(time_entries.keys()) == 1  # Only one day
        day_entries = list(time_entries.values())[0]
        pprint(day_entries)
        assert len(day_entries) == 2  # Only one TimeLog

        for entry in day_entries:
            assert isinstance(entry, TimeLog)
            assert len(entry.time_entries) == 1
