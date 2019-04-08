# Third Party Packages
import pytest

from toggl2harvest.models import HarvestCache


short_harvest_cache = {
    1: {
        'name': 'Awesome project',
        'client': {
            'id': 5,
            'name': 'Amazing Client',
        },
        'tasks': {
            7: 'Project Management',
            8: 'Development',
            9: 'Design',
        }
    },
}
mid_harvest_cache = {
    1: {
        'name': 'Awesome project',
        'client': {
            'id': 5,
            'name': 'Amazing Client',
        },
        'tasks': {
            7: 'Project Management',
            8: 'Development',
            9: 'Design',
        }
    },
    2: {
        'name': 'Awesome project',
        'client': {
            'id': 5,
            'name': 'Amazing Client',
        },
        'tasks': {
            70: 'Project Management',
            80: 'Development',
        }
    },
}


class TestHarvestCache:
    def test_harvest_cache(self):
        cache = HarvestCache(mid_harvest_cache)

        assert cache.tasks_by_name == {
            1: {
                'Project Management': 7,
                'Development': 8,
                'Design': 9,
            },
            2: {
                'Project Management': 70,
                'Development': 80,
            }
        }


class TestGetTaskId:
    @pytest.fixture
    def cache(self):
        return HarvestCache({
            1: {
                'name': 'Awesome project',
                'client': {
                    'id': 5,
                    'name': 'Amazing Client',
                },
                'tasks': {
                    7: 'Project Management',
                    8: 'Development',
                    9: 'Design',
                }
            },
        })

    def test_get_task_id(self, cache):
        task_id = cache.get_task_id(1, 'Project Management')

        assert task_id == 7

    def test_get_task_id_missing_project(self, cache):
        task_id = cache.get_task_id(2, 'Project Management')

        assert task_id is None

    def test_get_task_id_missing_task(self, cache):
        task_id = cache.get_task_id(1, 'Something thats not there')

        assert task_id is None


class TestTaskInProject:
    @pytest.fixture
    def cache(self):
        return HarvestCache({
            1: {
                'name': 'Awesome project',
                'client': {
                    'id': 5,
                    'name': 'Amazing Client',
                },
                'tasks': {
                    7: 'Project Management',
                    8: 'Development',
                    9: 'Design',
                }
            },
        })

    def test_task_in_project(self, cache):
        return cache.task_in_project(1, 7) is True

    def test_task_not_in_project(self, cache):
        return cache.task_in_project(1, 1) is False

    def test_not_valid_project(self, cache):
        return cache.task_in_project(2, 1) is False
