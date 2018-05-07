import datetime
from enum import Enum, auto

from modules import config


class Status(Enum):
    SUCCESS = auto()
    FAIL = auto()
    UNDEFINED = auto()


class ReportHandler:
    def __init__(self):
        self.report = open(config.REPORT, 'a+')
        self.report.seek(0)
        header = 'NAME, STATUS, REASON, COMMENT'
        if header not in self.report.read():
            self.report.write(header+'\n')

    def write(self, app_name, status, reason=None, comment=None):
        if not config.IGNORE_DONE_LIST:
            str = f'{app_name},{status.name}'
            if status in [Status.FAIL, Status.UNDEFINED]:
                str += f',{reason}'
            if comment is not None:
                str += f',{comment}'
            self.report.write(str + '\n')
            self.report.flush()

    def get_done_project_names(self):
        self.report.seek(0)
        done_project_names = [line.split(',')[0] for line in self.report.readlines() if 'UNDEFINED' not in line]
        return done_project_names

    def get_fail_counter(self):
        self.report.seek(0)
        fail_counter = self.report.read().count('FAIL')
        return fail_counter

    def close(self):
        self.report.close()

    def get_processed_apks(self):
        self.report.seek(0)
        return set([line.split(',')[0] for line in self.report.readlines()[1:]])


report_handler = ReportHandler()
