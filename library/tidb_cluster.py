from prometheus.prometheus_client import PrometheusClient
from prometheus.k8s_prom_query import K8sPromQueryInstance
from prometheus.cloud_prom_query import *
from utils import logger


class TiDBCluster:
    def __init__(self, conf):
        self.conf = conf
        self.cloud_prom_client = PrometheusClient(self.conf, 'cloud')
        self.k8s_prom_client = PrometheusClient(self.conf, 'k8s', False)
        self.logger = logger.setup_logger(__name__, conf['logging']['file_name'], conf['logging']['level'])

    def get_components_from_k8s(self):
        k8s = K8sPromQueryInstance(self.conf['cluster_info'])
        components = self.k8s_prom_client.get_vector_metrics_many(k8s.component_query)
        return components

    def get_components_from_cloud(self):
        components = self.cloud_prom_client.get_vector_metrics_many(component_query)
        self.logger.debug('components get from cloud: {}'.format(components))
        return components

    def validate_component(self, component):
        if component in self.get_components_from_cloud():
            return True
        else:
            return False
