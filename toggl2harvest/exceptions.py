class IncompleteHarvestData(Exception):
    pass


class MissingHarvestProject(IncompleteHarvestData):
    pass


class MissingHarvestTask(IncompleteHarvestData):
    pass


class InvalidHarvestTask(IncompleteHarvestData):
    pass


class InvalidHarvestProject(IncompleteHarvestData):
    pass


class InvalidFileError(Exception):
    pass
