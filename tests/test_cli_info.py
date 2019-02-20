import os
from os.path import expanduser

import pytest


from toggl2harvest.scripts.toggl2harvest import cli


def test_can_test_cli(cli_runner, credentials_file):
    result = cli_runner.invoke(cli, ['info'])

    print(result.output)
    assert result.exit_code == 0, result.output

    assert f'Configuration Directory: "."' in result.output



def test_can_set_config_dir_with_option(cli_runner, tmpdir, credentials_file):
    result = cli_runner.invoke(cli, [f'--config-dir={tmpdir}', 'info'])

    assert result.exit_code == 0, result.output
    assert f'Configuration Directory: "{tmpdir}"' in result.output


@pytest.mark.runner_setup(env={'TOGGL2HARVEST_CONFIG': '~/.toggl2harvest'})
def test_can_set_config_dir_with_env_var(cli_runner, credentials_file):
    result = cli_runner.invoke(cli, ['info'])

    full_path = expanduser('~/.toggl2harvest')
    assert result.exit_code == 0, result.output
    assert f'Configuration Directory: "{full_path}"' in result.output
