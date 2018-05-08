import logging
import time
from abc import ABC

from modules.decorators import log, exception

from modules import shell, config
from modules.entities import Type
from modules.testing_exceptions import InstallationException, StartCoverageException, TestingException, GrantStoragePermissionException, StopCoverageException, \
    RemoveApkException, CleaningException, GeneralException


class TimeTester(ABC):
    def __init__(self, apk, event_num=config.EVENT_NUM, seed=config.SEED, throttle=config.THROTTLE, test_num=config.TEST_NUM):
        self.apk = apk
        self.event_num = event_num
        self.seed = seed
        self.throttle = throttle
        self.test_num = test_num

    def test_apk(self):
        logging.debug('Apk path: ' + self.apk.path)
        elapsed_time = self.test()
        return elapsed_time

    def is_apk_instrumented(self):
        return self.apk.type == Type.INSTRUMENTED

    @log('CLEAN ADB')
    @exception(CleaningException)
    def clean_sdcard(self):
        shell.run(f'adb shell rm -rf /mnt/sdcard/{self.apk.package}.lock')
        shell.run(f'adb shell rm -rf /mnt/sdcard/{self.apk.package}')

    @log('INSTALL')
    @exception(InstallationException)
    def install_apk(self):
        shell.run(f'adb install -r {self.apk.path}')

    @log('START COVERAGE')
    @exception(StartCoverageException)
    def start_coverage(self):
        if self.is_apk_instrumented():
            logging.debug('in start coverage')
            shell.run_in_background(f'adb shell am instrument -e coverage true -w {self.apk.package}/com.zhauniarovich.bbtester.EmmaInstrumentation')

    @log('TEST')
    def test(self):
        times = []
        for n in range(self.test_num):
            self.remove_apk()
            self.clean_sdcard()
            self.install_apk()
            self.grant_storage_permission()
            self.start_coverage()
            try:
                start = time.time()
                self.run_monkey()
                end = time.time()
                elapsed_time = end - start
                times.append(elapsed_time)
            except GeneralException as e:
                logging.exception(f'{self.apk.package}, {self.apk.type}: {str(e)}, OUT: {e.out}')
                times.append(e)
            self.stop_coverage()
            self.remove_apk()
        return times

    @exception(TestingException)
    def run_monkey(self):
        shell.run(f'adb shell monkey -p {self.apk.package} -s {self.seed} --throttle {self.throttle} {self.event_num}')

    @log('STOP COVERAGE')
    @exception(StopCoverageException)
    def stop_coverage(self):
        if self.is_apk_instrumented():
            logging.debug('in stop coverage')
            shell.run(f"adb shell am broadcast -a 'com.zhauniarovich.bbtester.finishtesting'")

    @log('REMOVE APK')
    @exception(RemoveApkException, proceed_anyway=True)
    def remove_apk(self):
        shell.run(f'adb uninstall {self.apk.package}')
        self.remove_sdcard_data()

    @log('REMOVE SDCARD DATA', level=logging.DEBUG)
    def remove_sdcard_data(self):
        if self.apk.package in shell.run('adb shell ls /mnt/sdcard'):
            shell.run(f'adb shell rm -r /mnt/sdcard/{self.apk.package}')

    @log('GRANT PERMISSIONS')
    @exception(GrantStoragePermissionException)
    def grant_storage_permission(self):
        if self.is_apk_instrumented():
            shell.run(f'adb shell pm grant {self.apk.package} android.permission.WRITE_EXTERNAL_STORAGE')
            shell.run(f'adb shell pm grant {self.apk.package} android.permission.READ_EXTERNAL_STORAGE')



