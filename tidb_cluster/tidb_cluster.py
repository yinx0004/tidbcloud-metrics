import sys

import utils.helpers
from prometheus.prometheus_client import PrometheusClient
from prometheus.k8s_prom_query import K8sPromQueryInstance
from prometheus.cloud_prom_query import *
from utils import logger
from aws.aws_ec2_capacity import ec2_resource_capacity


class TiDBCluster:
    def __init__(self, conf):
        self.conf = conf
        self.cloud_prom_client = PrometheusClient(self.conf, 'cloud')
        self.k8s_prom_client = PrometheusClient(self.conf, 'k8s', False)
        self.logger = logger.setup_logger(__name__, conf['logging']['file_name'], conf['logging']['level'])
        self.conf['cluster_info']['access_points'] = self.get_access_point_from_cloud_prom()
        self.conf['cluster_info']['has_multi_access_point'] = self.has_multi_access_point()

    def get_components_from_k8s(self):
        k8s = K8sPromQueryInstance(self.conf['cluster_info'])
        components = self.k8s_prom_client.get_vector_metrics_many(k8s.component_query)
        return components

    def get_dedicated_clusters_by_tenant_from_k8s(self):
        cluster_list = []
        k8s = K8sPromQueryInstance(self.conf['cluster_info'])
        results = self.k8s_prom_client.get_vector_result_raw(k8s.dedicated_cluster_by_tenant_query)
        for result in results:
            cluster = {}
            cluster['tenant_id'] = result['metric']['label_tenant']
            cluster['project_id'] = result['metric']['label_project']
            cluster['cluster_id'] = result['metric']['label_cluster']
            self.logger.debug(cluster)
            cluster_list.append(cluster)
        self.logger.debug(cluster_list)
        cluster_list = utils.helpers.dictlist_deduplicate(cluster_list)
        return cluster_list

    def get_dedicated_clusters_by_project_from_k8s(self):
        cluster_list = []
        k8s = K8sPromQueryInstance(self.conf['cluster_info'])
        results = self.k8s_prom_client.get_vector_result_raw(k8s.dedicated_cluster_by_project_query)
        for result in results:
            cluster = {}
            cluster['tenant_id'] = result['metric']['label_tenant']
            cluster['project_id'] = result['metric']['label_project']
            cluster['cluster_id'] = result['metric']['label_cluster']
            self.logger.debug(cluster)
            cluster_list.append(cluster)
        self.logger.debug(cluster_list)
        cluster_list = utils.helpers.dictlist_deduplicate(cluster_list)
        return cluster_list

    def get_components_from_cloud(self):
        components = self.cloud_prom_client.get_vector_metrics_many(component_query)
        self.logger.debug('components get from cloud: {}'.format(components))
        return components

    def validate_component(self, component):
        if component in self.get_components_from_cloud():
            return True
        else:
            return False

    def get_instances_by_component(self, component):
        instances = []
        k8s = K8sPromQueryInstance(self.conf['cluster_info'], None, component)
        instances_info = self.k8s_prom_client.get_vector_result_raw(k8s.component_instance_query)
        for item in instances_info:
            instance = {}
            instance_name = item['metric']['label_kubernetes_io_hostname']
            instance_type = item['metric']['label_node_kubernetes_io_instance_type']
            instance[instance_name] = instance_type
            instances.append(instance)
        return instances

    def get_capacity_by_instance_type(self, instance_type):
        return ec2_resource_capacity[instance_type]

    def get_capacity_by_component(self, component):
        cloud = CloudPromComponentCapacityQuery()
        request = {}

        if component == 'tidb':
            request['CPU'] = cloud.tidb_cpu,
            request['Memory(GB)'] = cloud.tidb_memory
        elif component == 'pd':
            request['CPU'] = cloud.pd_cpu,
            request['Memory(GB)'] = cloud.pd_memory
        elif component == 'tikv':
            request['CPU'] = cloud.tikv_cpu,
            request['Memory(GB)'] = cloud.tikv_memory
            request['Storage(GB)'] = cloud.tikv_storage
        elif component == 'tiflash':
            request['CPU'] = cloud.tiflash_cpu,
            request['Memory(GB)'] = cloud.tiflash_memory
            request['Storage(GB)'] = cloud.tiflash_storage
        else:
            print('Unknown component {}'.format(component))
            return None

        capacity = {}
        for resource, query in request.items():
            res = self.cloud_prom_client.get_vector_metrics(query)
            self.logger.debug("capacity: {}".format(res))
            if res is not None:
                if resource != 'CPU':
                    capacity[resource] = res/1024/1024/1024
                else:
                    capacity[resource] = res
            else:
                self.logger.debug("No metrics")
                capacity = None

            return capacity

    def get_access_point_from_cloud_prom(self):
        cloud = CloudPromComponentMetricsQuery()
        tidb_uptime_metrics = self.cloud_prom_client.get_vector_result_raw(cloud.tidb_uptime)
        access_point_set = set()
        access_point_ids = []
        for item in tidb_uptime_metrics:
            instance_cluster = item['metric']['cluster']
            access_point_set.add(instance_cluster)
        for ac in access_point_set:
            if ac == 'db':
                access_point_ids.append('0')
            else:
                tmp = ac.split('-')
                access_point_ids.append(tmp[1])
        return access_point_ids

    def has_multi_access_point(self):
        if len(self.conf['cluster_info']['access_points']) > 1:
            return True
        else:
            return False

    def get_access_point_info(self):
        if self.has_multi_access_point():
            access_point_info = {}
            for access_point_id in self.conf['cluster_info']['access_points']:
                if access_point_id != '0':
                    access_point_info[access_point_id] = 'tidb-ac-%s' % access_point_id
                else:
                    access_point_info[access_point_id] = 'tidb'
            return access_point_info
        else:
            return None

    def get_access_point_tidb_component(self):
        return sorted(list(self.get_access_point_info().values()))