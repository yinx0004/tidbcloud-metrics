from utils import logger


class HealthAnalyzer:
    def __init__(self, conf):
        self.conf = conf
        self.logger = logger.setup_logger(__name__, conf['logging']['file_name'], conf['logging']['level'])

    def diagnose(self, metrics, thresholds):
        diagnostics = {}
        for metric, value in metrics.items():
            if metric not in thresholds or thresholds[metric] is None:
                note = "⚠️ Warning: threshold missing for "
                diagnostics[note + metric] = value
                self.logger.warning("threshold missing for metric {}".format(metric))
            elif value is None:
                note = "⚠️ Warning: metric empty for "
                diagnostics[note + metric] = value
                self.logger.warning("metric {} is None".format(metric))
            elif value <= thresholds[metric]:
                self.logger.info("{} passed".format(metric))
            else:
                note = "🚨 Critical: "
                diagnostics[note + metric] = value
                self.logger.warning("{}: {}, threshold: {}".format(metric, value, thresholds[metric]))

        return diagnostics

    def get_threshold(self, component):
        if component in self.conf['health']['threshold']:
            thresholds = self.conf['health']['threshold'][component]
        else:
            thresholds = None
        return thresholds
