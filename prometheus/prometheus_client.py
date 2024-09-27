from prometheus_api_client import PrometheusConnect
import sys
from utils import logger, helpers


class PrometheusClient:
    def __init__(self, conf, prom_type, auth=True):
        self.token = conf['prometheus']['cluster_prom_id_token']
        self.start_time = helpers.convert_datetime(conf['prometheus']['start_time'])
        self.end_time = helpers.convert_datetime(conf['prometheus']['end_time'])
        self.step = conf['prometheus']['step_in_seconds']
        self.auth = auth
        self.domain = conf['prometheus']['domain']
        self.operations = ["max", "average", "percentile_50", "percentile_75", "percentile_80", "percentile_85",
                        "percentile_90", "percentile_95", "percentile_99", "percentile_99.9"]
        
        self.logger = logger.setup_logger(__name__, conf['logging']['file_name'], conf['logging']['level'])
        self.conf = conf
        if prom_type == 'cloud':
            self.base_url = conf['prometheus']['cluster_prom_base_url']
            self.base_url = self.get_cluster_prom_base_url()
        elif prom_type == 'k8s':
            # print("k8s_prom_base_url"+conf['prometheus']['k8s_prom_base_url'])
            self.base_url = conf['prometheus']['k8s_prom_base_url']
        else:
            sys.exit('Invalid prom type')
        self.client = self.connect()

    def connect(self):
        if self.auth:
            client = PrometheusConnect(url=self.base_url, disable_ssl=False,
                                   headers={"Authorization": "bearer {}".format(self.token)})
            # serf.base_url='https://www.ds.us-east-1.aws.observability.tidbcloud.com/external/metrics/tidbcloud/tenant/1372813089193131282/project/1372813089206781474/application/1379661944646415465'
        else:
            client = PrometheusConnect(url=self.base_url, disable_ssl=False,
                                       headers=None)
        return client
    
    def get_resource_usage_metrics(self, request):
        if 'step' in request.keys():
            step = request['step']
        else:
            step = str(self.step)

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
        self.logger.debug("vector metrics: {}".format(res))
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

    def get_vector_result_raw(self, query):
        results = self.client.custom_query(query)
        return results

    def get_cluster_prom_base_url(self):
        
        base_url = "{}/tenant/{}/project/{}/application/{}".format(self.domain, self.conf['cluster_info']['tenant_id'], self.conf['cluster_info']['project_id'], self.conf['cluster_info']['cluster_id'])
        return base_url
    # def get_cluster_prom_url(self,tenant_id,project_id,cluster_id):
    #     return "{}/tenant/{}/project/{}/application/{}".format(self.domain, tenant_id, project_id, cluster_id)