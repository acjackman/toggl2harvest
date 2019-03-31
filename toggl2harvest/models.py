class TimeEntry:
    def __init__(self, start, end):
        self.start = start
        self.end = end


class TimeLog:
    def __init__(self, project_code, description, is_billable, time_entries):
        self.project_code = project_code
        self.description = description
        self.is_billable = is_billable
        self.time_entries = time_entries
