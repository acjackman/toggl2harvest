# Standard Library
from datetime import datetime

# Third Party Packages
import pytest

from toggl2harvest.scripts.toggl2harvest import cli


@pytest.fixture
def app_mock(mocker):
    return mocker.patch(
        'toggl2harvest.scripts.toggl2harvest.TogglHarvestApp'
    )


def test_cli_links_to_app(cli_runner, app_mock, mocker):
    result = cli_runner.invoke(
        cli,
        ['download-toggl-data'])

    assert result.exit_code == 0, result.output

    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    assert mocker.call().download_toggl_data(today, today) in app_mock.mock_calls
    assert mocker.call().write_time_entries(mocker.ANY) in app_mock.mock_calls


def test_cli_links_to_app_takes_start_end(cli_runner, app_mock, mocker):
    result = cli_runner.invoke(
        cli,
        ['download-toggl-data', '--start=2019-01-01', '--end=2019-01-01'])

    assert result.exit_code == 0, result.output

    date = datetime(2019, 1, 1)
    assert mocker.call().download_toggl_data(date, date) in app_mock.mock_calls


def test_cli_handles_bad_start(cli_runner, app_mock, mocker):
    result = cli_runner.invoke(
        cli,
        ['download-toggl-data', '--start=foo'])

    assert result.exit_code == 1, result.output
    assert '"foo" is not a valid start date' in result.output

    # Download shouldn't be called
    assert len(app_mock.mock_calls) == 1


def test_cli_handles_bad_end(cli_runner, app_mock, mocker):
    result = cli_runner.invoke(
        cli,
        ['download-toggl-data', '--end=bar'])

    assert result.exit_code == 1, result.output
    assert '"bar" is not a valid end date' in result.output

    # Download shouldn't be called
    assert len(app_mock.mock_calls) == 1
