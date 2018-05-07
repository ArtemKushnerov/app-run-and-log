from modules import shellhelper, agent
from modules.decorators import log
from modules.report_handler import report_handler, Status


class Tester:
    def __init__(self, apk):
        self.apk = apk

    def write_status(self, status, reason):
        report_handler.write(self.apk.name, status, reason)

    @log('UNINSTALL')
    def uninstall(self):
        shellhelper.uninstall(self.apk.package)

    @log('REPORT')
    def report_status(self):
        status, reason = agent.read_status_from_experimenter()
        return status, reason

    @log('RUN ACTIVITY')
    def run(self):
        self.apk.init_manifest()
        agent.run_main_activity(self.apk)

    @log('INSTALL')
    def install(self):
        shellhelper.install(self.apk.path)

    def test(self):
        self.install()
        self.run()
        status, reason = self.report_status()
        self.write_status(status, reason)
        self.uninstall()


