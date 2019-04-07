import pytest

from toggl2harvest.models import ProjectMapping


class TestIdentifyProjectInDescription:

    mappings = [
        ProjectMapping({
            'TEST': {},
        }),
        ProjectMapping({
            'TEST': {},
            'OTHER': {},
        }),
    ]

    @pytest.mark.parametrize('project_mapping', mappings)
    @pytest.mark.parametrize('description', [
        'TEST',
        'TEST-123',
        'TEST-123 — other text',
        'More text TEST-123',
        'TEST-123 Other text',
        'Other text TEST-123',
        'Other text TEST',
    ])
    def test_correct_description_match(self, project_mapping, description):
        result = project_mapping.project_in_description(description)

        assert result == 'TEST'

    def test_no_projects_returns_none(self):
        project_mapping = ProjectMapping({})

        result = project_mapping.project_in_description('TEST')

        assert result is None

    @pytest.mark.parametrize('project_mapping', mappings)
    def test_no_match_returns_none(self, project_mapping):
        result = project_mapping.project_in_description('THIRD')

        assert result is None

    @pytest.mark.parametrize('project_mapping', mappings)
    def test_description_none_returns_none(self, project_mapping):
        result = project_mapping.project_in_description(None)

        assert result is None
