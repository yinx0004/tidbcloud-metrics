from health_checker.reporter import Reporter
from health_checker.health_analyzer import HealthAnalyzer
from prometheus.cloud_prom_query import health_query
from prometheus.prometheus_client import PrometheusClient
from utils import logger
from library.tidb_cluster import TiDBCluster


class HealthChecker(TiDBCluster):
#class HealthChecker:
    #def __init__(self, conf, support_type):
    #    self.conf = conf
    #    self.logger = logger.setup_logger(__name__, conf['logging']['file_name'], conf['logging']['level'])
    #    self.analyzer = HealthAnalyzer(self.conf)
    #    self.client = PrometheusClient(self.conf, 'cloud')
    #    self.support_type = support_type

    def __init__(self, conf, check_type):
        super().__init__(conf)
        self.logger = logger.setup_logger(__name__, self.conf['logging']['file_name'], self.conf['logging']['level'])
        self.analyzer = HealthAnalyzer(self.conf)
        self.check_type = check_type

    def check_health(self, check_type, send_to=None):
        health_check_result = {}
        if check_type == "all":
            for component in self.check_type:
                if component != "all":
                    health_check_result[component] = self.check_component(component)

        else:
            health_check_result[check_type] = self.check_component(check_type)

        reporter = Reporter(self.conf)
        report = reporter.generate_report(health_check_result)
        if report is not None:
            self.logger.info("Health Check Report:\n\n{}".format(report))
        else:
            self.logger.error("No report generated")

        if send_to is not None:
            reporter.send_report(send_to)

    def check_resource(self):
        self.logger.info('Checking resource health')

    def check_component(self, component):
        result = {}
        self.logger.info('Checking {} health'.format(component))

        thresholds = self.analyzer.get_threshold(component)
        self.logger.debug("{} threshold: {}".format(component, thresholds))

        metrics = self.get_metrics(health_query[component])
        self.logger.debug("{} metrics: {}".format(component, metrics))
        result['metrics'] = metrics

        if thresholds is not None:
            result['diagnostics'] = self.analyzer.diagnose(metrics, thresholds)
            self.logger.debug("{} health check result: {}".format(component, result))
        else:
            result['diagnostics'] = "⚠️ Warning: {} threshold missing".format(component)

        if 'diagnostics' not in result or len(result['diagnostics']) == 0:
            result['diagnostics'] = "👍 All good!"
        return result

    def get_metrics(self, queries):
        metrics = {}
        for metric, query in queries.items():
            self.logger.debug("query: {}".format(query))
            result = self.cloud_prom_client.get_vector_metrics(query)
            metrics[metric] = result
        return metrics
