# Third Party Packages
import pytest

from toggl2harvest.exceptions import InvalidHarvestProject, InvalidHarvestTask
from toggl2harvest.models import HarvestCache, HarvestData, ProjectMapping, TimeLog


class TestUpdateHarvestTasks:

    @pytest.fixture
    def time_log(self):
        TimeLog(
            project_code=None,
            description=None,
            is_billable=True,
            time_entries=[],
        )

    @pytest.fixture
    def project_mapping(self):
        return ProjectMapping({
            'TEST': {
                'harvest': {
                    'project': 123,
                    'default_task': 'Development',
                }
            }
        })

    @pytest.fixture
    def harvest_cache(self):
        return HarvestCache([
            {
                'id': 123,
                'name': 'Test project',
                'tasks': {
                    15: {'name': 'Development'},
                    16: {'name': 'Task 6'},
                    17: {'name': 'Task 7'},
                },
            },
            {
                'id': 987,
                'name': 'Other Project',
                'tasks': {
                    95: {'name': 'Development'},
                    96: {'name': 'Task 6'},
                    97: {'name': 'Task 7'},
                },
            },
        ])

    def test_does_nothing_if_already_set(self, project_mapping, harvest_cache):
        time_log = TimeLog(
            project_code=None,
            description='description',
            is_billable=True,
            time_entries=[],
            harvest=HarvestData(
                project_id=987,
                task_id=97,
            ),
        )

        time_log.update_harvest_tasks(project_mapping, harvest_cache)

        assert time_log.harvest.project_id == 987
        assert time_log.harvest.task_id == 97

    def test_sets_default_task(self, project_mapping, harvest_cache):
        time_log = TimeLog(
            project_code=None,
            description='description',
            is_billable=True,
            time_entries=[],
            harvest=HarvestData(
                project_id=123,
                task_id=None,
            ),
        )

        time_log.update_harvest_tasks(project_mapping, harvest_cache)

        # Project hasn't changed
        assert time_log.harvest.project_id == 123
        # Task ID has been set
        assert time_log.harvest.task_id == 15

    def test_sets_based_on_task_name(self, project_mapping, harvest_cache):
        time_log = TimeLog(
            project_code=None,
            description='description',
            is_billable=True,
            time_entries=[],
            harvest=HarvestData(
                project_id=123,
                task_name='Task 6',
                task_id=None,
            ),
        )

        time_log.update_harvest_tasks(project_mapping, harvest_cache)

        # Project hasn't changed
        assert time_log.harvest.project_id == 123
        # Task ID has been set
        assert time_log.harvest.task_id == 16

    def test_errors_if_task_not_in_cache(self, project_mapping, harvest_cache):
        time_log = TimeLog(
            project_code=None,
            description='description',
            is_billable=True,
            time_entries=[],
            harvest=HarvestData(
                project_id=987,
                task_id=17,
            ),
        )

        with pytest.raises(InvalidHarvestTask):
            time_log.update_harvest_tasks(project_mapping, harvest_cache)

        assert time_log.harvest.project_id == 987
        assert time_log.harvest.task_id == 17

    def test_errors_if_project_not_in_cache(self, project_mapping, harvest_cache):
        time_log = TimeLog(
            project_code=None,
            description='description',
            is_billable=True,
            time_entries=[],
            harvest=HarvestData(
                project_id=1,
                task_id=None,
            ),
        )

        with pytest.raises(InvalidHarvestProject):
            time_log.update_harvest_tasks(project_mapping, harvest_cache)

        assert time_log.harvest.project_id == 1
        assert time_log.harvest.task_id is None

    def test_sets_based_on_project_code(self, project_mapping, harvest_cache):
        time_log = TimeLog(
            project_code='TEST',
            description='description',
            is_billable=True,
            time_entries=[],
            harvest=HarvestData(
                project_id=None,
                task_id=None,
            ),
        )

        time_log.update_harvest_tasks(project_mapping, harvest_cache)

        assert time_log.harvest.project_id == 123
        assert time_log.harvest.task_id == 15

    def test_sets_based_on_project_code_and_task_name(self, project_mapping, harvest_cache):
        time_log = TimeLog(
            project_code='TEST',
            description='description',
            is_billable=True,
            time_entries=[],
            harvest=HarvestData(
                project_id=None,
                task_name='Task 6',
                task_id=None,
            ),
        )

        time_log.update_harvest_tasks(project_mapping, harvest_cache)

        assert time_log.harvest.project_id == 123
        assert time_log.harvest.task_id == 16

    def test_sets_by_description_key(self, project_mapping, harvest_cache):
        time_log = TimeLog(
            project_code=None,
            description='TEST-9999 — and other text',
            is_billable=True,
            time_entries=[],
            harvest=HarvestData(
                project_id=None,
                task_id=None,
            ),
        )

        time_log.update_harvest_tasks(project_mapping, harvest_cache)

        assert time_log.harvest.project_id == 123
        assert time_log.harvest.task_id == 15
        assert time_log.description == 'TEST-9999 — and other text'
