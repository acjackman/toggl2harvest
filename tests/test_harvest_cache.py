import pytest
from inspect import cleandoc as trim_multiline

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

        assert cache.task_ids == {
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
