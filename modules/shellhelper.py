import logging
import subprocess
import psutil

from modules import config
from modules.exceptions import AbsentPackageException, ErrorInstallingException, ErrorUninstallingException, NotEnoughSpaceException


def install(new_apk_path):
    cmd = '"%s" install -r "%s"' % (config.ADB_PATH, new_apk_path)
    try:
        out = run(cmd)
    except subprocess.CalledProcessError as e:
        if 'not enough space' in str(e):
            raise NotEnoughSpaceException()
        raise ErrorInstallingException(e.output.decode('utf-8'))
    if 'Exception occurred while dumping' in out:
        raise ErrorUninstallingException


def uninstall(package):
    cmd = '"%s" uninstall "%s"' % (config.ADB_PATH, package)
    try:
        request_pipe(cmd)
    except Exception:
        raise ErrorUninstallingException


def get_package(path):
    cmd = f'aapt dump badging {path}'
    try:
        out = request_pipe(cmd)
    except Exception:
        raise AbsentPackageException()
    first_line = out.split('\n')[0]
    name_attribute = first_line.split(' ')[1]
    package = name_attribute.split('=')[1]
    package = package.replace("'", '')
    return package


def request_pipe(cmd):
    pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = pipe.communicate()

    res = out
    if not out:
        res = err

    if pipe.returncode > 0 :
        raise Exception("----------------------------------------------------\n\
Out: %s\nError: %s" % (out, err))

    return res.decode('utf-8')


def run(command):
    out = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    return out.decode('utf-8')


def run_in_background(command):
    return subprocess.Popen(command, shell=True)


def start_activity_explicitly(package_name, activity_name):
    # adb shell am start -n com.package.name/com.package.name.ActivityName
    logging.debug("Starting activity [%s] of the package [%s]..." % (activity_name, package_name))

    run_string = package_name + '/' + activity_name
    cmd = "{0} shell am start -n {1}".format(config.ADB_PATH, run_string)
    request_pipe(cmd)