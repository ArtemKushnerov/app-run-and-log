import logging
import os
from os import listdir
import subprocess

import shutil

import time

from modules import config, shellhelper
from modules.report_handler import report_handler, Status
from abc import ABC, abstractmethod


class Preparator(ABC):
    def __init__(self):
        super().__init__()
        self.apks_dir = config.APK_REPOSITORY
        self.test_dir = config.TEST_REPOSITORY
        self.previous_report = config.PREVIOUS_REPORT
        self.apks = [f for f in listdir(self.apks_dir) if f.endswith('.apk') and self.apk_succeded(f)]
        self.error_type = None

    def prepare(self):
        logging.info(f'Preparing {len(self.apks)}')
        for apk in self.apks:
            try:
                self.prepare_apk(apk)
            except subprocess.CalledProcessError as e:
                output = e.output.decode("utf-8")
                logging.exception(f'{self.error_type} for {apk}. Out: {output}')
                report_handler.write(apk.replace('.apk', ''), Status.FAIL, reason=f'{self.error_type}', comment=output.replace('\n', ' ').strip())
            except Exception as e:
                logging.exception(f'{self.error_type} for {apk}')
                report_handler.write(apk.replace('.apk', ''), Status.FAIL, reason=f'{self.error_type}', comment=str(e).replace('\n', ' ').strip())
        self.finish_preparation()

    @abstractmethod
    def prepare_apk(self, apk):
        pass

    @abstractmethod
    def finish_preparation(self):
        pass

    def apk_succeded(self, apk):
        succeeded = False
        with open(self.previous_report) as report:
            succeeded = f'{apk},SUCCESS' in report.read()
        return succeeded


class SignPreparator(Preparator):

    def __init__(self):
        super().__init__()
        self.error_type = 'SIGNING ERROR'
        self.keystore = 'e:\google_play0306\my-keystore.jks'

    def prepare_apk(self, apk):
        logging.debug(f'signing {apk}')
        shellhelper.run(fr'apksigner sign --ks {self.keystore} --ks-pass pass:123456 --out {self.test_dir}\{apk} {self.apks_dir}\{apk}')

    def finish_preparation(self):
        logging.info('Finishing signing  preparation')


class RebuildingPreparator(Preparator):
    def __init__(self):
        super().__init__()
        self.error_type = 'REBUILDING_ERROR'
        self.keystore = 'e:\google_play0306\my-keystore.jks'

    def prepare_apk(self, apk):
        logging.debug(f'Build {apk}')
        shellhelper.run(fr'apktool --quiet build {config.SOURCES_REPOSITORY}\{apk.replace(".apk", "")} -o {self.test_dir}\raw\{apk}')
        logging.debug(f'Align {apk}')
        shellhelper.run(fr'zipalign -f -v 4 {self.test_dir}\raw\{apk} {self.test_dir}\aligned\{apk}')
        logging.debug(f'Resign {apk}')
        shellhelper.run(fr'apksigner sign --ks {self.keystore} --ks-pass pass:123456 --out {self.test_dir}\{apk} {self.test_dir}\aligned\{apk}')

    def finish_preparation(self):
        logging.info('Finishing rebuilding  preparation')


class InstrumentPreparator(Preparator):
    def __init__(self):
        super().__init__()
        self.error_type = 'INSTRUMENTATION_ERROR'
        self.ACVTOOL_PATH = r"C:\SaToSS\Sources\droidmod-smali-modifier"
        self.ACVTOOL_PYTHON = r"c:\Python27\python.exe"
        self.APK_REPOSITORY = r"d:\google_play\1-play-apks"
        self.ACVTOOL_RESULTS = r"d:\google_play\4-instrumented_apks"
        self.ACVTOOL_WD = r"C:\SaToSS\Sources\droidmod-smali-modifier\smiler\acvtool_working_dir"
        self.result_json_file = 'results.json'
        self.instrumentation_time_file = open(os.path.join(self.test_dir, 'instrumetation-time.csv'),'a+')
        header = 'NAME,TIME'
        self.instrumentation_time_file.seek(0)
        if header not in self.instrumentation_time_file.read():
            self.instrumentation_time_file.write(header + "\n")

    def prepare_apk(self, apk):
        self.instrument(apk)
        pkg = apk.replace(".apk", "")
        self.move_files(pkg)

    def instrument(self, apk):
        smiler = os.path.join(self.ACVTOOL_PATH, 'smiler', 'acvtool.py')
        start = time.time()
        logging.debug(f'Instrument {apk}')
        shellhelper.run(fr'{self.ACVTOOL_PYTHON} {smiler} instrument -r --wd {self.ACVTOOL_WD} {config.APK_REPOSITORY}\{apk}')
        finish = time.time()
        time_elapsed = finish - start
        logging.info(f'Time elapsed: {time_elapsed}')
        self.instrumentation_time_file.write(f'{apk}, {time_elapsed}\n')
        self.instrumentation_time_file.flush()

    def move_files(self, pkg):
        pickle = os.path.join(self.ACVTOOL_WD, "metadata", pkg + ".pickle")
        instrumented_apk = os.path.join(self.ACVTOOL_WD, "instr_" + pkg + ".apk")
        android_manifest = os.path.join(self.ACVTOOL_WD, "apktool", "AndroidManifest.xml")
        if os.path.exists(pickle) and os.path.exists(instrumented_apk) and os.path.exists(android_manifest):
            shutil.copyfile(pickle, os.path.join(self.test_dir, pkg + ".pickle"))
            shutil.copyfile(instrumented_apk, os.path.join(self.test_dir, pkg + ".apk"))
            shutil.copyfile(android_manifest, os.path.join(self.test_dir, pkg + ".xml"))
        else:
            raise Exception(f"Not all required files are present for a {pkg}")

    def finish_preparation(self):
        logging.info('Finishing instrumentation preparation')
        self.instrumentation_time_file.close()


sign_preparator = SignPreparator()
rebuilding_preparator = RebuildingPreparator()
instrument_preparator = InstrumentPreparator()