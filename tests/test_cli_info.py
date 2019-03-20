# Standard Library
from os.path import expanduser

# Third Party Packages
import pytest

from toggl2harvest.scripts.toggl2harvest import cli


def test_can_set_config_dir_with_option(cli_runner, tmpdir, credentials_file):
    result = cli_runner.invoke(cli, [f'--config-dir={tmpdir}', 'info'])

    assert result.exit_code == 0, result.output
    assert f'Configuration Directory: "{tmpdir}"' in result.output


@pytest.mark.runner_setup(env={'TOGGL2HARVEST_CONFIG': '~/.some_dot_folder'})
def test_can_set_config_dir_with_env_var(cli_runner, credentials_file):
    result = cli_runner.invoke(cli, ['info'])

    full_path = expanduser('~/.some_dot_folder')
    assert result.exit_code == 0, result.output
    assert f'Configuration Directory: "{full_path}"' in result.output
