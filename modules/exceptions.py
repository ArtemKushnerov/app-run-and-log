class RunAndLogException(Exception):
    def __init__(self, cause=None):
        self.cause = cause.strip()


class AbsentActivityException(RunAndLogException):
    pass


class ManifestNotFoundException(RunAndLogException):
    pass


class UserExitException(RunAndLogException):
    pass


class AbsentPackageException(RunAndLogException):
    pass


class ErrorInstallingException(RunAndLogException):
    pass


class ErrorUninstallingException(RunAndLogException):
    pass


class NotEnoughSpaceException(RunAndLogException):
    pass

class RemoveApkException(RunAndLogException):
    pass
