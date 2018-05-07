import datetime
import logging.config
import sys

import os

import psutil
import yaml

from modules import shellhelper, preparators
from modules import config
from modules.report_handler import report_handler, Status
from modules.entities import Apk
from modules.exceptions import AbsentActivityException, ManifestNotFoundException, UserExitException, ErrorInstallingException, ErrorUninstallingException, NotEnoughSpaceException
from modules.tester import Tester

def setup_logging():
    with open('logging.yaml') as f:
        logging.config.dictConfig(yaml.safe_load(f.read()))


def main():
    logging.info("START EXPERIMENT")
    # preparators.instrument_preparator.prepare()
    apks = set(f for f in os.listdir(config.TEST_REPOSITORY) if f.endswith('.apk'))
    processed_apks = report_handler.get_processed_apks()
    apps_to_process = apks - processed_apks
    overall_apps = len(apks)
    fail_counter = report_handler.get_fail_counter()
    counter = len(processed_apks)

    logcat_proc = capture_logcat_output()
    try:
        for app_name in apps_to_process:
            logging.info('================================================================================================================================================')
            apk = Apk(app_name)
            tester = Tester(apk)
            try:
                counter += 1
                logging.info(f'{app_name}: {counter} OF {overall_apps}, FAIL TO RUN: {fail_counter}')
                tester.test()
            except ErrorInstallingException as e:
                fail_counter += 1
                logging.exception(f'Cannot install app {app_name}')
                report_handler.write(app_name, Status.FAIL, reason='INSTALLATION ERROR', comment=f'{e.cause}')
            except NotEnoughSpaceException:
                logging.exception(f'Cannot install app {app_name} because there is not enough space. Stopping tool. Please, wipe data, then run tool again')
                sys.exit()
            except AbsentActivityException:
                fail_counter += 1
                logging.exception(f'Absent main activity for app {app_name}')
                tester.uninstall()
                report_handler.write(app_name, Status.FAIL, reason='ABSENT ACTIVITY')
            except ManifestNotFoundException:
                fail_counter += 1
                logging.error(f'Manifest not found for app {app_name}')
                report_handler.write(app_name, Status.FAIL, reason='MANIFEST NOT FOUND')
                tester.uninstall()
            except UserExitException:
                logging.info(f'User has chosen to exit while testing {app_name}')
                report_handler.write(app_name, Status.UNDEFINED, reason='USER_EXIT')
                tester.uninstall()
                sys.exit()
            except ErrorUninstallingException:
                logging.exception(f'Cannot uninstall {app_name}')
                report_handler.write(app_name, Status.SUCCESS, comment='UNINSTALL ERROR')
            except BaseException:
                fail_counter += 1
                logging.exception(f'Exception for app {app_name}')
                tester.uninstall()
                report_handler.write(app_name, Status.FAIL, reason='UNKNOWN')

        report_handler.close()
    finally:
        try:
            kill(logcat_proc.pid)
        except Exception:
            logging.warning('Exception during logcat process kill')



def capture_logcat_output():
    shellhelper.run('adb logcat -c')
    timestamp = '{:%Y%m%d}'.format(datetime.date.today())
    logcat_name = os.path.join(config.TEST_REPOSITORY, f'logcat{timestamp}.txt')
    return shellhelper.run_in_background(f'adb logcat > {logcat_name}')

def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()


if __name__ == "__main__":
    setup_logging()
    main()
