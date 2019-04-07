# Standard Library
from datetime import datetime as dt
from inspect import cleandoc as trim_multiline
from pathlib import Path

# Third Party Packages
import pytest

from toggl2harvest.app import TogglHarvestApp


@pytest.fixture
def app(credentials_file):
    return TogglHarvestApp()


class TestCredFile:
    def test_default_path_correct(self, app):
        assert app.cred_file == Path('.', 'credentials.yaml')

    @pytest.mark.parametrize('config_dir', [
        '2019-01-01',
        'foobar',
    ])
    def test_correct_path(self, app, config_dir):
        app.config_dir = config_dir
        assert app.cred_file == Path(config_dir, 'credentials.yaml')

    def test_cred_file_returns_same_instance(self, app):
        instance_1 = app.cred_file
        instance_2 = app.cred_file
        assert instance_1 is instance_2


class TestDataDir:
    def test_default_path_correct(self, app):
        assert app.data_dir == Path('.', 'data')

    @pytest.mark.parametrize('config_dir', [
        '2019-01-01',
        'foobar',
    ])
    def test_correct_path(self, app, config_dir):
        app.config_dir = config_dir
        assert app.data_dir == Path(config_dir, 'data')

    def test_cred_file_returns_same_instance(self, app):
        instance_1 = app.data_dir
        instance_2 = app.data_dir
        assert instance_1 is instance_2


class TestDataFile:
    @pytest.mark.parametrize('datestr,full_path', [
        ('2019-01-01', './data/2019-01-01.yml'),
        ('foobar', './data/foobar.yml'),
    ])
    def test_correct_path(self, mocker, datestr, full_path, app):
        assert app.data_file(datestr) == Path(full_path)


class TestTogglCred:
    def test_toggl_cred_calls_correct_function(self, mocker, app):
        cred_file = mocker.patch.object(app, 'cred_file')
        mock = mocker.patch('toggl2harvest.toggl.TogglCredentials.read_from_file')

        app.toggl_cred

        mock.assert_called_with(cred_file)

    def test_toggl_cred_returns_same_instance(self, mocker, app):
        mocker.patch.object(app, 'cred_file')
        mocker.patch('toggl2harvest.toggl.TogglCredentials.read_from_file')

        instance_1 = app.toggl_cred
        instance_2 = app.toggl_cred

        assert instance_1 is instance_2


class TestHarvestCred:
    def test_harvest_cred_calls_correct_function(self, mocker, app):
        cred_file = mocker.patch.object(app, 'cred_file')
        mock = mocker.patch('toggl2harvest.harvest.HarvestCredentials.read_from_file')

        app.harvest_cred

        mock.assert_called_with(cred_file)

    def test_harvest_cred_returns_same_instance(self, mocker, app):
        mocker.patch.object(app, 'cred_file')
        mocker.patch('toggl2harvest.harvest.HarvestCredentials.read_from_file')

        instance_1 = app.harvest_cred
        instance_2 = app.harvest_cred

        assert instance_1 is instance_2


class TestTogglAPI:
    def test_toggl_api_calls_correct_function(self, mocker, app):
        mock_cred = mocker.PropertyMock()
        app.toggl_cred = mock_cred
        mock = mocker.patch('toggl2harvest.toggl.TogglSession.__init__', return_value=None)

        app.toggl_api

        mock.assert_called_with(mock_cred)


class TestHarvestAPI:
    def test_harvest_api_calls_correct_function(self, mocker, app):
        mock_cred = mocker.PropertyMock()
        app.harvest_cred = mock_cred
        mock = mocker.patch('toggl2harvest.harvest.HarvestSession.__init__', return_value=None)

        app.harvest_api

        mock.assert_called_with(mock_cred)


class TestProjectFile:
    @pytest.mark.parametrize('config_dir', [
        '2019-01-01',
        'foobar',
    ])
    def test_project_file(self, mocker, app, config_dir):
        app.config_dir = config_dir
        assert app.project_file == Path(config_dir, 'project_mapping.yml')


class TestProjectMapping:
    def test_project_mapping(self, mocker, app):
        app.project_file = trim_multiline("""
        PROJ:
            harvest_project: 123
            default_task: Task Name
        """)

        assert app.project_mapping == {
            'PROJ': {
                'harvest_project': 123,
                'default_task': 'Task Name',
            }
        }


class TestCacheHarvestProjects:
    def test_calls_correct_function(self, mocker, app):
        mock_api = mocker.PropertyMock()
        app.harvest_api = mock_api

        app.cache_harvest_projects()

        mock_api.update_project_cache.assert_called_with(app.config_dir)


class TestDownloadTogglData:
    def test_calls_correct_function(self, mocker, app):
        mock_cred_file = mocker.PropertyMock()
        app.cred_file = mock_cred_file
        mock_data_dir = mocker.PropertyMock()
        app.data_dir = mock_data_dir
        mock_api = mocker.PropertyMock()
        mock_api.toggl_download_params.return_value = {'fake': 'params'}
        mock_api.retrieve_time_entries.return_value = [{'entry': 1}, {'entry': 2}]
        app.toggl_api = mock_api

        app.download_toggl_data(dt(2019, 1, 1), dt(2019, 1, 1))

        mock_api.toggl_download_params.assert_called_with(mock_cred_file)
        mock_api.retrieve_time_entries.assert_called_with(
            dt(2019, 1, 1),
            dt(2019, 1, 1),
            params={'fake': 'params'},
        )
        mock_api.write_report_data.assert_called_with(
            [{'entry': 1}, {'entry': 2}],
            mock_data_dir,
        )
