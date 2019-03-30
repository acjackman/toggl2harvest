from inspect import cleandoc

# Third Party Packages
import pytest

from toggl2harvest import toggl

@pytest.fixture
def toggl_credentials():
    return toggl.TogglCredentials(
        api_token='123',
        workspace_id=123,
        user_agent='123',
    )

@pytest.fixture
def toggl_session(toggl_credentials):
    return toggl.TogglSession(toggl_credentials)


class TestTogglSession:
    def test_toggl_download_params(self, toggl_session):
        params = toggl_session.toggl_download_params(cleandoc(
        """
        toggl:
          dowload_data_params:
            project_ids: '123'
        """
        ))

        assert params == {'project_ids': '123'}

    @pytest.mark.parametrize('file_contents', [
        # No Toggl key
        """
        bob_ross:
            dowload_data_params: 'abc'
        """,
        # No download params
        """
        toggl:
            api_token: 'abc'
        """,
        # Params not an object
        """
        toggl:
            dowload_data_params: 'abc'
        """,
        """
        toggl:
            dowload_data_params:
                - foo
                - bar
        """,
    ])
    def test_toggl_download_errors(self, toggl_session, file_contents):
        params = toggl_session.toggl_download_params(
            cleandoc(file_contents)
        )

        assert params == {}

    def test_toggl_download_params_file_not_exists(self, toggl_session, tmpdir):
        params = toggl_session.toggl_download_params(tmpdir.join('not_real.yml'))

        assert params == {}

