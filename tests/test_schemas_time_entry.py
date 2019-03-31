# Standard Library
from datetime import datetime as dt
from datetime import timezone

# Third Party Packages
import pytest
from dateutil.tz import tzoffset
from marshmallow.exceptions import ValidationError

from toggl2harvest import models, schemas


PLUS_2 = tzoffset(None, 7200)
MINUS_7 = tzoffset(None, -25200)

def make_valid_time_entries(valid_tuples):
    return [
        ({'s': s, 'e': e}, models.TimeEntry(start, end))
        for s, start, e, end in valid_tuples
    ]

class TestTimeEntrySchema:
    @pytest.fixture
    def schema(self):
        return schemas.TimeEntrySchema()

    valid_data = make_valid_time_entries([
        (
            '2019-01-01T12:00:00+00:00',
            dt(2019, 1, 1, 12, tzinfo=timezone.utc),
            '2019-01-01T12:30:00+00:00',
            dt(2019, 1, 1, 12, 30, tzinfo=timezone.utc),
        ),
        (
            '2019-01-01T12:00:00+00:00',
            dt(2019, 1, 1, 12, tzinfo=timezone.utc),
            '2019-01-01T12:30:00+00:00',
            dt(2019, 1, 1, 12, 30, tzinfo=timezone.utc),
        ),
        (
            '2019-01-01T12:00:00-07:00',
            dt(2019, 1, 1, 12, tzinfo=MINUS_7),
            '2019-01-01T12:30:00-07:00',
            dt(2019, 1, 1, 12, 30, tzinfo=MINUS_7),
        ),
        (
            '2019-01-01T12:00:00+02:00',
            dt(2019, 1, 1, 12, tzinfo=PLUS_2),
            '2019-01-01T12:30:00+02:00',
            dt(2019, 1, 1, 12, 30, tzinfo=PLUS_2),
        ),
    ])

    @pytest.mark.parametrize('valid_data,time_entry', valid_data)
    def test_serialize(self, schema, valid_data, time_entry):
        serialized = schema.dump(time_entry)
        assert serialized == valid_data

    @pytest.mark.parametrize('valid_data,time_entry', valid_data +
        make_valid_time_entries([
            (
                '2019-01-01T12:00:00-0700',
                dt(2019, 1, 1, 12, tzinfo=MINUS_7),
                '2019-01-01T12:30:00-0700',
                dt(2019, 1, 1, 12, 30, tzinfo=MINUS_7),
            ),
        ])
    )
    def test_deserialize(self, schema, valid_data, time_entry):
        new_obj = schema.load(valid_data)

        assert new_obj.start == time_entry.start
        assert new_obj.end == time_entry.end

    invalid_data = [
        # Invalid values
        {
            's': 1,
            'e': 2,
        },
        {
            's': '2019-01-01T12:00:00+00:00',
            'e': 2,
        },
        {
            's': '2019-01-01T12:00:00+00:00',
            'e': None,
        },
        {
            's': 1,
            'e': '2019-01-01T12:30:00+0000',
        },
        {
            's': None,
            'e': '2019-01-01T12:30:00+0000',
        },
        # Wrong variables names
        {
            'start': '2019-01-01T12:00:00+0000',
            'end': '2019-01-01T12:30:00+0000',
        },
    ]

    @pytest.mark.parametrize('invalid_data', invalid_data)
    def test_deserialize_invalid_data(self, schema, invalid_data):
        with pytest.raises(ValidationError):
            schema.load(invalid_data)
