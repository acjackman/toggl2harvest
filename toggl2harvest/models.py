class TimeEntry:
    def __init__(self, start, end):
        self.start = start
        self.end = end


class TogglData:
    def __init__(self, client=None, project=None, task=None, is_billable=None):
        self.client = client
        self.project = project
        self.task = task
        self.is_billable = is_billable


class HarvestData:
    def __init__(self, project_id=None, task_name=None, task_id=None, uploaded=None):
        self.project_id = project_id
        self.task_name = task_name
        self.task_id = task_id
        self.uploaded = uploaded


class TimeLog:
    def __init__(
        self, project_code, description, is_billable, time_entries,
        toggl=None, harvest=None
    ):
        self.project_code = project_code
        self.description = description
        self.is_billable = is_billable
        self.time_entries = time_entries
        self.toggl = toggl or TogglData()
        self.harvest = harvest or HarvestData()
