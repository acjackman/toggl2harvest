# Standard Library
import logging
import os
from inspect import cleandoc as trim_multiline

# Third Party Packages
import pytest


@pytest.fixture(autouse=True)
def logging_config(caplog):
    caplog.set_level(logging.DEBUG)


@pytest.fixture
def credentials_file(tmpdir):
    cred_file_path = tmpdir.join('credentials.yaml')
    contents = trim_multiline(
        """
        harvest:
          account_id: '123'
          token: 'token'
          user_agent: 'user@example.com'
        toggl:
          api_token: 'token'
          workspace_id: 123
          user_agent: 'user@example.com'
          params:
            project_ids: ["0", "1"]
        """
    )
    os.chdir(tmpdir)
    with open(cred_file_path, 'w') as f:
        f.write(contents)

    return cred_file_path
