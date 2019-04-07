class IncompleteHarvestData(Exception):
    pass


class MissingHarvestProject(IncompleteHarvestData):
    pass


class MissingHarvestTask(IncompleteHarvestData):
    pass
