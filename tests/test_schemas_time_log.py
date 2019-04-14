# Standard Library
import collections
from datetime import datetime as dt
from datetime import timezone

# Third Party Packages
import pytest
from marshmallow.exceptions import ValidationError

from toggl2harvest import models, schemas


TimeLogData = collections.namedtuple(
    'TimeLogData',
    ' '.join([
        'project_code',
        'description',
        'is_billable',
        'time_entries_serialized',
        'time_entries_data',
    ])
)


def make_valid_time_log(valid_tuples):
    return [
        ({
            'project_code': vt.project_code,
            'description': vt.description,
            'is_billable': vt.is_billable,
            'time_entries': vt.time_entries_serialized,
            'toggl': {
                'client': None,
                'project': None,
                'task': None,
                'is_billable': None,
            },
            'harvest': {
                'project_id': None,
                'task_name': None,
                'task_id': None,
                'uploaded': None,
            }
        },
            models.TimeLog(
            project_code=vt.project_code,
            description=vt.description,
            is_billable=vt.is_billable,
            time_entries=vt.time_entries_data,
        ))
        for vt in valid_tuples
    ]


class TestTimeEntrySchema:
    @pytest.fixture
    def schema(self):
        return schemas.TimeLogSchema()

    valid_data = make_valid_time_log([
        TimeLogData(
            project_code=None,
            description=None,
            is_billable=False,
            time_entries_serialized=None,
            time_entries_data=None,
        ),
        TimeLogData(
            project_code=None,
            description=None,
            is_billable=False,
            time_entries_serialized=[],
            time_entries_data=[],
        ),
        TimeLogData(
            project_code=None,
            description=None,
            is_billable=False,
            time_entries_serialized=[
                {
                    's': '2019-01-01T12:00:00+00:00',
                    'e': '2019-01-01T12:30:00+00:00',
                },
            ],
            time_entries_data=[
                models.TimeEntry(
                    dt(2019, 1, 1, 12, tzinfo=timezone.utc),
                    dt(2019, 1, 1, 12, 30, tzinfo=timezone.utc),
                ),
            ],
        ),
        TimeLogData(
            project_code=None,
            description=None,
            is_billable=False,
            time_entries_serialized=[
                {
                    's': '2019-01-01T12:00:00+00:00',
                    'e': '2019-01-01T12:30:00+00:00',
                },
                {
                    's': '2019-01-01T13:00:00+00:00',
                    'e': '2019-01-01T13:30:00+00:00',
                },
            ],
            time_entries_data=[
                models.TimeEntry(
                    dt(2019, 1, 1, 12, tzinfo=timezone.utc),
                    dt(2019, 1, 1, 12, 30, tzinfo=timezone.utc),
                ),
                models.TimeEntry(
                    dt(2019, 1, 1, 13, tzinfo=timezone.utc),
                    dt(2019, 1, 1, 13, 30, tzinfo=timezone.utc),
                ),
            ],
        ),
    ])

    @pytest.mark.parametrize('valid_data,time_log', valid_data)
    def test_serialize(self, schema, valid_data, time_log):
        serialized = schema.dump(time_log)

        assert serialized == valid_data

    @pytest.mark.parametrize('valid_data,time_log', valid_data)
    def test_deserialize(self, schema, valid_data, time_log):
        new_obj = schema.load(valid_data)

        assert new_obj.project_code == time_log.project_code
        assert new_obj.description == time_log.description
        assert new_obj.is_billable == time_log.is_billable
        assert isinstance(new_obj.toggl, models.TogglData)
        assert isinstance(new_obj.harvest, models.HarvestData)

    invalid_data = [
        # Invalid values
        {
            'project_code': None,
            'description': None,
            'is_billable': None,
        },
        # Missing Key Names
        {
            'project_code': None,
            'description': None,
            'time_entries': None,
        },
    ]

    @pytest.mark.parametrize('invalid_data', invalid_data)
    def test_deserialize_invalid_data(self, schema, invalid_data):
        with pytest.raises(ValidationError):
            schema.load(invalid_data)
