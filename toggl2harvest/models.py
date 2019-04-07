# Standard Library
import logging


log = logging.getLogger(__name__)


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


class IncompleteHarvestData(Exception):
    pass


class MissingHarvestProject(IncompleteHarvestData):
    pass


class MissingHarvestTask(IncompleteHarvestData):
    pass


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

    def update_harvest_project_task(self):
        if self.harvest.project_id is None:
            log.debug('harvest.project_id not found')

    def update_harvest_tasks(self, project_mapping, harvest_cache):
        # Get or set harvest project
        if self.harvest.project_id is None:
            log.debug('harvest.project_id not found')
            try:
                harvest_proj = project_mapping.harvest_project(self.project_code)
                self.harvest.project_id = harvest_proj
            except KeyError:
                raise MissingHarvestProject()
        else:
            harvest_proj = self.harvest.project_id

        # Set harvest task
        if self.harvest.task_id is None:
            log.debug('harvest.task_id not found')
            task_name = self.harvest.task_name
            if self.harvest.task_name is None or self.harvest.task_name == '':
                raise MissingHarvestTask()

            try:
                self.harvest.task_id = harvest_cache.get_task_id(harvest_proj, task_name)
            except KeyError:
                raise MissingHarvestTask()
        return


class ProjectMapping:
    def __init__(self, mapping):
        self.mapping = mapping

    def harvest_project(self, project_code):
        return self.mapping[project_code]['harvest_project']

    def default_harvest_task(self, project_code):
        return


class HarvestCache:
    def __init__(self, harvest_cache):
        self.task_ids = {}
        for project_id, v in harvest_cache.items():
            self.task_ids[project_id] = {
                name: task_id
                for task_id, name in v['tasks'].items()
            }

    def get_task_id(self, proj_id, task_name):
        return self.task_ids[proj_id][task_name]
