class GeneralException(Exception):
    def __init__(self, out):
        self.out = out
        self.type = self.__class__.__name__

    def __str__(self):
        return f'{self.type}'

class CleaningException(GeneralException):
    pass

    
class InstallationException(GeneralException):
    pass


class StartCoverageException(GeneralException):
    pass


class TestingException(GeneralException):
    pass


class PullCoverageException(GeneralException):
    pass


class GrantStoragePermissionException(GeneralException):
    pass


class StopCoverageException(GeneralException):
    pass


class GenerateReportException(GeneralException):
    pass


class BuildDirDetectFailException(GeneralException):
    pass


class PullCrashReportExceptException(GeneralException):
    pass


class RemoveApkException(GeneralException):
    pass




