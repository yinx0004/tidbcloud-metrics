from prometheus_api_client import PrometheusConnect
import sys
from utils import logger, helpers


class PrometheusClient:
    def __init__(self, conf, prom_type, auth=True):
        if prom_type == 'cloud':
            self.base_url = conf['prometheus']['cluster_prom_base_url']
        elif prom_type == 'k8s':
            self.base_url = conf['prometheus']['k8s_prom_base_url']
        else:
            sys.exit('Invalid prom type')

        self.token = conf['prometheus']['cluster_prom_id_token']
        self.start_time = helpers.convert_datetime(conf['prometheus']['start_time'])
        self.end_time = helpers.convert_datetime(conf['prometheus']['end_time'])
        self.step = conf['prometheus']['step_in_seconds']
        self.auth = auth
        self.operations = ["max", "average", "percentile_50", "percentile_75", "percentile_80", "percentile_85",
                        "percentile_90", "percentile_95", "percentile_99", "percentile_99.9"]
        self.logger = logger.setup_logger(__name__, conf['logging']['file_name'], conf['logging']['level'])
        self.client = self.connect()

    def connect(self):
        if self.auth:
            client = PrometheusConnect(url=self.base_url, disable_ssl=False,
                                   headers={"Authorization": "bearer {}".format(self.token)})
        else:
            client = PrometheusConnect(url=self.base_url, disable_ssl=False,
                                       headers=None)
        return client

    def get_resource_usage_metrics(self, request):
        if 'step' in request.keys():
            step = request['step']
        else:
            step = str(self.step)

        self.logger.debug("step={}, type={}".format(step, type(step)))
        res = self.client.get_metric_aggregation(
            query=request['query_metric'],
            start_time=self.start_time, end_time=self.end_time, step=step,
            operations=self.operations)
        return res

    def get_resource_capacity_metrics(self, request):
        res = self.client.custom_query(request['query_capacity'], params={'timeout': 60})
        return res

    def get_capacity_n_count(self, request):
        res = self.client.custom_query(request['query_capacity'])
        self.logger.debug("capacity and count: {}".format(res))
        if res is not None and len(res) > 0:
            instance_cnt = len(res)
            value = res[0]['value']
            capacity = value[1]
            return capacity, instance_cnt
        else:
            self.logger.debug("No metrics")
            return None, None

    def get_metrics(self, query):
        res = self.client.custom_query(query)
        return res

    def get_vector_metrics(self, query):
        res = self.client.custom_query(query)
        #self.logger.debug("vector metrics: {}".format(res))
        if res is not None and len(res) > 0:
            return float(res[0]['value'][1])
        else:
            return None

    def get_vector_metrics_many(self, query):
        metrics = {}
        results = self.client.custom_query(query)
        if results is not None and len(results) > 0:
            for result in results:
                for k, v in result['metric'].items():
                    metrics[v] = result['value'][1]
        return metrics
