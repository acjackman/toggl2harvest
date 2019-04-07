# Standard Library
import re
import logging

from .exceptions import (
    MissingHarvestProject,
    MissingHarvestTask,
    InvalidHarvestTask,
    InvalidHarvestProject,
)


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

    def _identify_harvest_project(self, project_mapping):
        project_id = self.harvest.project_id
        if project_id is None and self.project_code:
            project_id = project_mapping.harvest_project(self.project_code)

        if project_id is None:
            project_code = project_mapping.project_in_description(self.description)
            project_id = project_mapping.harvest_project(project_code)

        if project_id is None:
            raise MissingHarvestProject()

        return project_id

    def _identify_harvest_task(self, project_mapping, harvest_cache):
        harvest_proj = self.harvest.project_id
        assert harvest_proj is not None

        if self.harvest.task_id is not None:
            return self.harvest.task_id

        default_task_name = project_mapping.harvest_task_default(harvest_proj)
        task_name = self.harvest.task_name or default_task_name
        if task_name is None or task_name == '':
            raise MissingHarvestTask()

        try:
            return harvest_cache.get_task_id(harvest_proj, task_name)
        except KeyError:
            raise MissingHarvestTask()

    def update_harvest_tasks(self, project_mapping, harvest_cache):
        self.harvest.project_id = self._identify_harvest_project(project_mapping)

        if not harvest_cache.project_in_cache(self.harvest.project_id):
            raise InvalidHarvestProject()

        self.harvest.task_id = self._identify_harvest_task(project_mapping, harvest_cache)

        if not harvest_cache.task_in_project(self.harvest.project_id, self.harvest.task_id):
            raise InvalidHarvestTask()


class ProjectMapping:
    def __init__(self, mapping):
        self.mapping = mapping
        self.default_tasks = {}
        for code, project in mapping.items():
            try:
                p_id = project['harvest']['project']
                t_name = project['harvest']['default_task']
                self.default_tasks[p_id] = t_name
            except KeyError:
                pass

        self.project_re = re.compile(f'({"|".join(mapping.keys())})(-[0-9]+)?')

    def harvest_project(self, project_code):
        try:
            return self.mapping[project_code]['harvest']['project']
        except KeyError:
            return None

    def harvest_task_default(self, harvest_proj):
        try:
            return self.default_tasks[harvest_proj]
        except KeyError:
            return None

    def project_in_description(self, description):
        if description is None:
            return None

        # regular expression doesn't work if there are no project keys
        if len(self.mapping) == 0:
            return None

        for match in self.project_re.finditer(description):
            return match.groups(0)[0]


class HarvestCache:
    def __init__(self, harvest_cache):
        self.tasks_by_name = {}
        self.project_tasks = {}
        for project_id, v in harvest_cache.items():
            self.tasks_by_name[project_id] = {
                name: task_id
                for task_id, name in v['tasks'].items()
            }
            self.project_tasks[project_id] = set(v['tasks'].keys())

    def project_in_cache(self, proj_id):
        try:
            return self.tasks_by_name[proj_id]
        except KeyError:
            return None

    def get_task_id(self, proj_id, task_name):
        try:
            return self.tasks_by_name[proj_id][task_name]
        except KeyError:
            return None

    def task_in_project(self, proj_id, task_id):
        try:
            return task_id in self.project_tasks[proj_id]
        except KeyError:
            return False
