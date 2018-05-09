import datetime
import logging.config

import os

import psutil
import yaml

from modules import shell
from modules import config
from modules.report_handler import report_handler
from modules.entities import Apk, Type
from modules.time_tester import TimeTester

def setup_logging():
    with open('logging.yaml') as f:
        logging.config.dictConfig(yaml.safe_load(f.read()))


class ContinueException(Exception):
    pass


def main():
    logging.info("START EXPERIMENT")
    apks = set(f for f in os.listdir(config.TEST_REPOSITORY) if f.endswith('.apk'))
    processed_apks = set([apk + '.apk' for apk in report_handler.get_processed_apks()])
    apps_to_process = apks - processed_apks
    overall_apps = len(apks)
    counter = len(processed_apks)

    logcat_proc = capture_logcat_output()
    try:
        for app_name in apps_to_process:
            try:
                logging.info('================================================================================================================================================')
                apk_instrumented = Apk(app_name, type=Type.INSTRUMENTED)
                apk_original = Apk(app_name, type=Type.ORIGINAL)
                logging.info(f'{app_name}: {counter} OF {overall_apps}')
                result = {}
                for apk in (apk_original, apk_instrumented):
                    tester = TimeTester(apk)
                    try:
                        time = tester.test_apk()
                        logging.debug('time:' + str(time))
                        result[apk.type] = time
                    except Exception as e:
                        tester.remove_apk()
                        logging.exception(f'{apk.package}, {apk.type}: {str(e)}')
                        raise ContinueException
                    finally:
                        tester.remove_apk()
                logging.debug('Result: ' + str(result))
                report_handler.write(apk_original.package, original_time=result[Type.ORIGINAL], instrumented_time=result[Type.INSTRUMENTED])
                counter += 1
            except ContinueException:
                logging.debug('Continue after exception')
    finally:
        report_handler.close()
        try:
            kill(logcat_proc.pid)
        except Exception:
            logging.warning('Exception during logcat process kill')


def capture_logcat_output():
    shell.run('adb logcat -c')
    timestamp = '{:%Y%m%d}'.format(datetime.date.today())
    logcat_name = os.path.join(config.TEST_REPOSITORY, f'logcat{timestamp}.txt')
    return shell.run_in_background(f'adb logcat > {logcat_name}')


def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()


if __name__ == "__main__":
    setup_logging()
    main()
