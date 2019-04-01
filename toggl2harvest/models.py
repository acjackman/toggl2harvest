class TimeEntry:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    @classmethod
    def build_from_toggl_entry(cls, report_entry):
        return TimeEntry(
            start=report_entry.start,
            end=report_entry.end,
        )

class TogglReportEntry:
    def __init__(
        self, client, project, task, description, is_billable, start, end, tags=[]
    ):
        self.client = client
        self.project = project
        self.task = task
        self.description = description
        self.is_billable = is_billable
        self.start = start
        self.end = end
        self.tags = tags

    def unique_key(self):
        return (
            self.client,
            self.project,
            self.task,
            self.description,
            self.is_billable,
        )


class TogglData:
    def __init__(self, client=None, project=None, task=None, is_billable=None):
        self.client = client
        self.project = project
        self.task = task
        self.is_billable = is_billable

    def unique_key(self):
        return (
            self.client,
            self.project,
            self.task,
            self.description,
            self.is_billable,
        )


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

    @classmethod
    def build_from_toggl_entry(cls, report_entry):
        return TimeLog(
            project_code=None,
            description=report_entry.description,
            is_billable=report_entry.is_billable,
            time_entries=[
                TimeEntry(report_entry.start, report_entry.end),
            ],
            toggl=TogglData(
                client=report_entry.client,
                project=report_entry.project,
                task=report_entry.task,
                is_billable=report_entry.is_billable,
            )
        )

    def add_to_time_entries(self, report_entry):
        assert report_entry.unique_key() == self.toggl.unique_key()
        entry = TimeEntry.build_from_toggl_entry(report_entry)
        self.time_entries.append(entry)
        return entry
