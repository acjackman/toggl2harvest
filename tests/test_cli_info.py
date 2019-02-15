import pytest

from toggl2harvest.scripts.toggl2harvest import cli


def test_can_test_cli(cli_runner):
    result = cli_runner.invoke(cli, ['info'])

    assert result.exit_code == 0, result.output
    assert 'Configuration Directory: "~/.toggl2harvest"' in result.output


def test_can_set_config_dir_with_option(isolated_cli_runner):
    result = isolated_cli_runner.invoke(cli, ['--config-dir=.', 'info'])

    assert result.exit_code == 0, result.output
    assert 'Configuration Directory: "."' in result.output


@pytest.mark.runner_setup(env={'TOGGL2HARVEST_CONFIG': '.'})
def test_can_set_config_dir_with_env_var(isolated_cli_runner):
    result = isolated_cli_runner.invoke(cli, ['info'])

    assert result.exit_code == 0, result.output
    assert 'Configuration Directory: "."' in result.output
