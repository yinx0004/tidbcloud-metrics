from prometheus_api_client import PrometheusConnect
import sys
from utils import logger, helpers


class PrometheusClient:
    def __init__(self, base_url, start_time, end_time, step_in_seconds, log_file_name, log_level, token=None):
        self.base_url = base_url
        self.token = token
        self.start_time = helpers.convert_datetime(start_time)
        self.end_time = helpers.convert_datetime(end_time)
        self.step = step_in_seconds
        self.operations = ["max", "average", "percentile_50", "percentile_75", "percentile_80", "percentile_85",
                        "percentile_90", "percentile_95", "percentile_99", "percentile_99.9"]
        self.logger = logger.setup_logger(__name__, log_file_name, log_level)
        self.client = self.connect()

    def connect(self):
        if self.token is None:
            client = PrometheusConnect(url=self.base_url, disable_ssl=False,
                                       headers=None)
        else:
            client = PrometheusConnect(url=self.base_url, disable_ssl=False,
                                   headers={"Authorization": "bearer {}".format(self.token)})
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
        res = self.client.custom_query(request['query_capacity'])
        return res

    def get_capacity_n_count(self, request):
        res = self.client.custom_query(request['query_capacity'])
        if res is not None:
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
