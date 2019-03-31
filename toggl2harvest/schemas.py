# Third Party Packages
from marshmallow import Schema, fields, post_load

from . import models


class TimeEntrySchema(Schema):
    s = fields.LocalDateTime(attribute="start")
    e = fields.LocalDateTime(attribute="end")

    @post_load
    def make_user(self, data):
        return models.TimeEntry(**data)
