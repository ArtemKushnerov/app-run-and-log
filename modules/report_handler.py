import numbers
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
        header = 'NAME'
        for num in range(1, config.TEST_NUM + 1):
            header += f',OR{num}'
        for num in range(1, config.TEST_NUM + 1):
            header += f',IN{num}'
        header += f',AVG_OR'
        header += f',AVG_IN'
        header += f',DIFF'

        if header not in self.report.read():
            self.report.write(header+'\n')

    def write(self, app_name, original_time, instrumented_time):
        if not config.IGNORE_DONE_LIST:
            line = f'{app_name}'

            sum_or = 0
            or_num = 0
            for or_time in original_time:
                if isinstance(or_time, numbers.Number):
                    line += ',{:.4f}'.format(or_time)
                    sum_or += or_time
                    or_num += 1
                else:
                    line += ',' + str(or_time)

            sum_in = 0
            in_num = 0
            for in_time in instrumented_time:
                if isinstance(in_time, numbers.Number):
                    line += ',{:.4f}'.format(in_time)
                    sum_in += in_time
                    in_num += 1
                else:
                    line += ',' + str(in_time)

            avg_or = sum_or / or_num if or_num else 0
            avg_in = sum_in / in_num if in_num else 0
            diff = avg_in - avg_or

            line += ',{:.4f}'.format(avg_or)
            line += ',{:.4f}'.format(avg_in)
            line += ',{:.4f}'.format(diff)

            self.report.write(line + '\n')
            self.report.flush()

    def close(self):
        self.report.close()

    def get_processed_apks(self):
        self.report.seek(0)
        return set([line.split(',')[0] for line in self.report.readlines()[1:]])


report_handler = ReportHandler()
