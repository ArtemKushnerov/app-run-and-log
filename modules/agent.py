import logging
import os
import sys

from modules import shellhelper
from modules.report_handler import Status
from modules.exceptions import AbsentActivityException, UserExitException



def run_main_activity(apk):
    main_activity_name = apk.manifest.getMainActivity()
    if main_activity_name is None:
        raise AbsentActivityException
    logging.debug(f'Manifest path: {apk.manifest.pathAndroidManifest}')
    shellhelper.start_activity_explicitly(apk.manifest.packageName, main_activity_name)


def read_status_from_experimenter():
    print("Press: c - crashed, s - successed, e - exit")
    key = wait_key()
    while key != 's' and key != 'c' and key != 'e':
        print("Press: c - crashed, s - successed, e - exit")
        key = wait_key()
    if key == 'e':
        raise UserExitException()

    status, reason = None, None
    if key == 's':
        status = Status.SUCCESS
    elif key == 'c':
        status = Status.FAIL
        reason = 'CRASHED'
    return status, reason



def wait_key():
    ''' Wait for a key press on the console and return it. '''
    result = None
    if os.name == 'nt':
        import msvcrt
        result = msvcrt.getch()
    else:
        import termios
        fd = sys.stdin.fileno()
        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)
        try:
            result = sys.stdin.read(1)
        except IOError:
            pass
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
    return result.decode('utf-8')
