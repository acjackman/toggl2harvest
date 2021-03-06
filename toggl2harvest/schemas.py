# Third Party Packages
from marshmallow import EXCLUDE, Schema, fields, post_load

from . import models


class TimeEntrySchema(Schema):
    s = fields.LocalDateTime(attribute='start')
    e = fields.LocalDateTime(attribute='end')

    @post_load
    def make_time_entry(self, data):
        return models.TimeEntry(**data)


class TogglDataSchema(Schema):
    client = fields.Str(required=False, allow_none=True)
    project = fields.Str(required=False, allow_none=True)
    task = fields.Str(required=False, allow_none=True)
    is_billable = fields.Boolean(required=False, allow_none=True)

    @post_load
    def make_toggl_data(self, data):
        return models.TogglData(**data)


class TogglReportEntrySchema(Schema):
    class Meta:
        unknown = EXCLUDE
    client = fields.Str(required=False, allow_none=True)
    project = fields.Str()
    task = fields.Str(required=False, allow_none=True)
    description = fields.Str(required=False, allow_none=True)
    is_billable = fields.Boolean()
    start = fields.LocalDateTime()
    end = fields.LocalDateTime()
    tags = fields.List(fields.Str(), required=False, allow_none=True)

    @post_load
    def make_toggl_report_entry(self, data):
        return models.TogglReportEntry(**data)


class HarvestDataSchema(Schema):
    project_id = fields.Integer(required=False, allow_none=True)
    task_name = fields.Str(required=False, allow_none=True)
    task_id = fields.Integer(required=False, allow_none=True)
    uploaded = fields.DateTime(required=False, allow_none=True)

    @post_load
    def make_harvest_data(self, data):
        return models.HarvestData(**data)


class TimeLogSchema(Schema):
    project_code = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    is_billable = fields.Boolean(required=True)
    time_entries = fields.Nested(TimeEntrySchema, allow_none=True, many=True)
    toggl = fields.Nested(TogglDataSchema, required=False)
    harvest = fields.Nested(HarvestDataSchema, required=False)

    @post_load
    def make_time_log(self, data):
        return models.TimeLog(**data)


class HarvestCacheTaskSchema(Schema):
    name = fields.Str(required=True)
    link_active = fields.Boolean(required=False, allow_none=True)


class HarvestCacheClientSchema(Schema):
    id = fields.Integer()
    name = fields.Str()


class HarvestCacheEntrySchema(Schema):
    id = fields.Integer()
    name = fields.Str()
    active = fields.Boolean()
    client = fields.Nested(HarvestCacheClientSchema)
    code = fields.Str(required=False, allow_none=True)
    tasks = fields.Dict(
        keys=fields.Integer(),
        values=fields.Nested(HarvestCacheTaskSchema))
