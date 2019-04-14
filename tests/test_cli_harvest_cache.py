# Third Party Packages
import pytest

from toggl2harvest.scripts.toggl2harvest import cli


@pytest.fixture
def app_mock(mocker):
    return mocker.patch(
        'toggl2harvest.scripts.toggl2harvest.TogglHarvestApp'
    )


def test_cli_links_to_app(cli_runner, app_mock, mocker):
    app_mock.cache_harvest_projects = mocker.MagicMock()

    result = cli_runner.invoke(
        cli,
        ['harvest-cache'])

    assert result.exit_code == 0, result.output

    assert mocker.call().cache_harvest_projects() in app_mock.mock_calls
