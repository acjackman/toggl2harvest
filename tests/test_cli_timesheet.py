# Third Party Packages
import pytest

from toggl2harvest.scripts.toggl2harvest import cli


@pytest.fixture
def app_mock(mocker):
    return mocker.patch(
        'toggl2harvest.scripts.toggl2harvest.TogglHarvestApp'
    )


@pytest.fixture
def validate_mock(mocker):
    return mocker.patch(
        'toggl2harvest.scripts.toggl2harvest._validate_time_logs'
    )


@pytest.fixture
def upload_mock(mocker):
    return mocker.patch(
        'toggl2harvest.scripts.toggl2harvest._upload_to_harvest'
    )


def test_cli_upload(cli_runner, app_mock, mocker, validate_mock, upload_mock):
    app_mock.download_toggl_data = mocker.MagicMock()

    result = cli_runner.invoke(
        cli,
        ['timesheet'], input='n')

    assert result.exit_code == 0, result.output

    assert validate_mock.call_count == 1
    assert upload_mock().call_count == 0
    assert mocker.call().download_toggl_data(mocker.ANY, mocker.ANY) in app_mock.mock_calls


def test_cli_links_to_app(cli_runner, app_mock, mocker, validate_mock, upload_mock):
    app_mock.download_toggl_data = mocker.MagicMock()

    result = cli_runner.invoke(
        cli,
        ['timesheet'], input='y')

    assert result.exit_code == 0, result.output

    assert validate_mock.call_count == 1
    assert upload_mock.call_count == 1
    assert mocker.call().download_toggl_data(mocker.ANY, mocker.ANY) in app_mock.mock_calls
