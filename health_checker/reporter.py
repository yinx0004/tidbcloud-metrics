from utils import logger, helpers
import pprint

class Reporter:
    def __init__(self, conf):
        self.logger = logger.setup_logger(__name__, conf['logging']['file_name'], conf['logging']['level'])
        self.report = ''

    def generate_report(self, health_check_result):
        self.logger.info("Generating report")
        self.report = helpers.dict_to_yaml(health_check_result)
        return self.report

    def send_report(self, channel):
        if channel == 'email':
            pass
        elif channel == 'lark':
            pass
        elif channel == 'slack':
            pass
        elif channel == 'console':
            pass
        else:
            self.logger.error("Not supported report channel")