import pytest

from toggl2harvest.scripts.toggl2harvest import cli
from toggl2harvest.harvest import HarvestCredentials


@pytest.fixture()
def fake_harvest_cred():
    return HarvestCredentials('acount_id', 'token', 'user-agent')


@pytest.fixture()
def harvest_cred_mock(mocker, fake_harvest_cred):
    return mocker.patch(
        'toggl2harvest.harvest.HarvestCredentials.read_from_file',
        return_value=fake_harvest_cred
    )


@pytest.fixture()
def harvest_session_mock(mocker, fake_harvest_cred):
    return mocker.patch(
        'toggl2harvest.harvest.HarvestSession.update_project_cache',
    )


@pytest.mark.runner_setup(env={'TOGGL2HARVEST_CONFIG': '.'})
def test_harvest_cred_fails_gracefully_with_no_credentials_file(
        mocker, isolated_cli_runner, harvest_session_mock):

    result = isolated_cli_runner.invoke(
        cli,
        ['harvest-cache'])

    print(result.output)
    assert result.exit_code == 1, result.output

    assert harvest_session_mock.call_count == 0


@pytest.mark.runner_setup(env={'TOGGL2HARVEST_CONFIG': '.'})
def test_harvest_cred_fails_gracefully_with_malformed_credentials_file(
        mocker, isolated_cli_runner, harvest_session_mock):
    with open('credentials.yaml', 'w') as f:
        f.write('abcdef')

    result = isolated_cli_runner.invoke(
        cli,
        ['-v', 'harvest-cache'])

    print(result.output)
    assert result.exit_code == 1, result.output

    assert harvest_session_mock.call_count == 0
    pytest.fail('see output')

@pytest.mark.runner_setup(env={'TOGGL2HARVEST_CONFIG': '.'})
def test_harvest_cred_updates_project_cache(
        mocker, isolated_cli_runner, harvest_cred_mock, harvest_session_mock):
    result = isolated_cli_runner.invoke(
        cli,
        ['harvest-cache'])

    assert result.exit_code == 0, result.output

    assert harvest_cred_mock.call_count == 1
    harvest_cred_mock.assert_called_with('./credentials.yaml')

    assert harvest_session_mock.call_count == 1
    harvest_session_mock.assert_called_with('.')
