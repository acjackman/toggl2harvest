# Third Party Packages
from marshmallow import Schema, fields, post_load

from . import models


class TimeEntrySchema(Schema):
    s = fields.LocalDateTime(attribute="start")
    e = fields.LocalDateTime(attribute="end")

    @post_load
    def make_user(self, data):
        return models.TimeEntry(**data)


class TimeLogSchema(Schema):
    project_code = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    is_billable = fields.Boolean(required=True)
    time_entries = fields.Nested(TimeEntrySchema, allow_none=True, many=True)

    @post_load
    def make_user(self, data):
        return models.TimeLog(**data)
