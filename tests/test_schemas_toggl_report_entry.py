# Standard Library
import collections
from datetime import datetime as dt
from datetime import timezone

# Third Party Packages
import pytest
from marshmallow.exceptions import ValidationError

from toggl2harvest import models, schemas, utils

TogglReportData = collections.namedtuple(
    'TogglReportData',
    ' '.join([
        'client',
        'project',
        'task',
        'description',
        'is_billable',
        'start',
        'end',
        'tags',
    ])
)


def make_valid_toggl_entry(valid_tuples):
    return [
        ({
            'client': vt.client,
            'project': vt.project,
            'task': vt.task,
            'description': vt.description,
            'is_billable': vt.is_billable,
            'start': vt.start,
            'end': vt.end,
            'tags': vt.tags,
        },
            models.TogglReportEntry(
                client=vt.client,
                project=vt.project,
                task=vt.task,
                description=vt.description,
                is_billable=vt.is_billable,
                start=utils.strp_iso8601(vt.start),
                end=utils.strp_iso8601(vt.end),
                tags=vt.tags,
        ))
        for vt in valid_tuples
    ]


class TestTogglReportEntrySchema:
    @pytest.fixture
    def schema(self):
        return schemas.TogglReportEntrySchema()

    valid_data = make_valid_toggl_entry([
        TogglReportData(
            client='client name',
            project='project name',
            task='task name',
            description='description goes here',
            is_billable=False,
            start='2019-03-25T06:00:17-06:00',
            end='2019-03-25T08:21:17-06:00',
            tags=[],
        ),
        TogglReportData(
            client='client name',
            project='project name',
            task='task name',
            description='description goes here',
            is_billable=True,
            start='2019-03-25T06:00:17-06:00',
            end='2019-03-25T08:21:17-06:00',
            tags=['single_tag'],
        ),
        TogglReportData(
            client='client name',
            project='project name',
            task='task name',
            description='description goes here',
            is_billable=False,
            start='2019-03-25T06:00:17-06:00',
            end='2019-03-25T08:21:17-06:00',
            tags=['many', 'tags'],
        ),
    ])

    @pytest.mark.parametrize('valid_data,toggl_entry', valid_data)
    def test_serialize(self, schema, valid_data, toggl_entry):
        serialized = schema.dump(toggl_entry)

        assert serialized == valid_data

    @pytest.mark.parametrize('valid_data,toggl_entry', valid_data)
    def test_deserialize(self, schema, valid_data, toggl_entry):
        new_obj = schema.load(valid_data)

        assert new_obj.client == toggl_entry.client
        assert new_obj.project == toggl_entry.project
        assert new_obj.task == toggl_entry.task
        assert new_obj.description == toggl_entry.description
        assert new_obj.is_billable == toggl_entry.is_billable
        assert new_obj.start == toggl_entry.start
        assert new_obj.end == toggl_entry.end
        assert new_obj.tags == toggl_entry.tags

    invalid_data = [
        # Invalid values
        {
            'client': None,
            'project': None,
            'task': None,
            'description': None,
            'is_billable': None,
            'start': None,
            'end': None,
            'tags': None,
        },
    ]

    @pytest.mark.parametrize('invalid_data', invalid_data)
    def test_deserialize_invalid_data(self, schema, invalid_data):
        with pytest.raises(ValidationError):
            schema.load(invalid_data)
