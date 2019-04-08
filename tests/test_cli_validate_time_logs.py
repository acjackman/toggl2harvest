# Third Party Packages
import pytest
from datetime import datetime

from toggl2harvest.app import TogglHarvestApp
from toggl2harvest.scripts.toggl2harvest import cli, _validate_time_logs


@pytest.fixture
def app_mock(mocker):
    return mocker.patch(
        'toggl2harvest.scripts.toggl2harvest.TogglHarvestApp'
    )


def test_cli_links_to_app(cli_runner, app_mock, mocker):
    vtl_mock = mocker.patch('toggl2harvest.scripts.toggl2harvest'
                            '._validate_time_logs')

    result = cli_runner.invoke(
        cli,
        ['validate-time-logs'])

    assert result.exit_code == 0, result.output

    today = datetime.today()
    vtl_mock.assert_called_with(mocker.ANY, [f'{today:%Y-%m-%d}'])


def test_cli_handles_bad_start(cli_runner, app_mock, mocker):
    result = cli_runner.invoke(
        cli,
        ['validate-time-logs', '--start=foo'])

    assert result.exit_code == 1, result.output
    assert '"foo" is not a valid start date' in result.output

    # Download shouldn't be called
    assert len(app_mock.mock_calls) == 1


def test_cli_handles_bad_end(cli_runner, app_mock, mocker):
    result = cli_runner.invoke(
        cli,
        ['validate-time-logs', '--end=bar'])

    assert result.exit_code == 1, result.output
    assert '"bar" is not a valid end date' in result.output

    # Download shouldn't be called
    assert len(app_mock.mock_calls) == 1


@pytest.fixture
def app(tmpdir):
    return TogglHarvestApp(config_dir=tmpdir)


def test_validate_time_log_interior(app, mocker):
    vf_mock = mocker.patch.object(app, 'validate_file', return_value=0)

    _validate_time_logs(app, ['2019-01-01'])

    assert vf_mock.call_count == 1


def test_validate_time_log_interior_error_edits_file(app, mocker):
    edit_mock = mocker.patch('toggl2harvest.scripts.toggl2harvest.click.edit')
    confirm_mock = mocker.patch(
        'toggl2harvest.scripts.toggl2harvest.click.confirm',
        return_value=True)
    vf_mock = mocker.patch.object(app, 'validate_file', side_effect=[1, 0])

    _validate_time_logs(app, ['2019-01-01'])

    assert edit_mock.call_count == 1
    assert confirm_mock.call_count == 1
    assert vf_mock.call_count == 2
