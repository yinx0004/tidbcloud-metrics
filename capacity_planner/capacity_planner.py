import sys

from utils import logger, helpers
from prometheus.prometheus_client import PrometheusClient
from prometheus.k8s_prom_query import K8sPromQueryInstance, K8sPromQueryBatchInstanceMetrics
from prometheus.cloud_prom_query import CloudPromComponentMetricsQuery, CloudPromComponentCapacityQuery
from capacity_planner.metrics_analyzer import MetricsAnalyzer
from capacity_planner.aws_ec2_capacity import ec2_resource_capacity
from datetime import datetime


class CapacityPlanner:
    def __init__(self, conf):
        self.conf = conf
        self.logger = logger.setup_logger(__name__, self.conf['logging']['file_name'], self.conf['logging']['level'])
        self.csv_file_name = "data/{}_capacity_plan_{}.csv".format(self.conf['cluster_info']['cluster_id'], self.conf['time'])
        self.csv_file_fields = ['component', 'name', 'max', 'average', 'percentile_50.0', 'percentile_75.0', "percentile_80.0",
                       "percentile_85.0", "percentile_90.0", "percentile_95.0", 'percentile_99.0', 'percentile_99.9',
                       'capacity', 'instance_cnt', 'plan_max', 'plan_average', 'plan_percentile_50.0',
                       'plan_percentile_75.0', 'plan_percentile_80.0', 'plan_percentile_85.0', 'plan_percentile_90.0',
                       'plan_percentile_95.0', 'plan_percentile_99.0', 'plan_percentile_99.9']

    def cluster_prom_capacity_plan(self):
        client = PrometheusClient(self.conf, 'cloud')
        metrics_query = CloudPromComponentMetricsQuery()
        capacity_query = CloudPromComponentCapacityQuery()

        # Add 'step' key for customized interval
        requests = [
            {'component': 'tidb', 'name': 'CPU(core)', 'query_metric': metrics_query.tidb_cpu,
             'query_capacity': capacity_query.tidb_cpu},
            {'component': 'tidb', 'name': 'Memory(byte)', 'query_metric': metrics_query.tidb_memory,
             'query_capacity': capacity_query.tidb_memory},
            {'component': 'tikv', 'name': 'CPU(core)', 'query_metric': metrics_query.tikv_cpu,
             'query_capacity': capacity_query.tikv_cpu},
            {'component': 'tikv', 'name': 'Memory(byte)', 'query_metric': metrics_query.tikv_memory,
             'query_capacity': capacity_query.tikv_memeory},
            {'component': 'tikv', 'name': 'Storage(byte)', 'query_metric': metrics_query.tikv_storage,
             'query_capacity': capacity_query.tikv_storage},
            {'component': 'pd', 'name': 'CPU(core)', 'query_metric': metrics_query.pd_cpu,
             'query_capacity': capacity_query.pd_cpu},
            {'component': 'pd', 'name': 'Memory(byte)', 'query_metric': metrics_query.pd_memory,
             'query_capacity': capacity_query.pd_memory},
            {'component': 'tiflash', 'name': 'CPU(core)', 'query_metric': metrics_query.tiflash_cpu,
             'query_capacity': capacity_query.tiflash_cpu},
            {'component': 'tiflash', 'name': 'Memory(byte)', 'query_metric': metrics_query.tiflash_memory,
             'query_capacity': capacity_query.tiflash_memory},
            {'component': 'tiflash', 'name': 'Storage(byte)', 'query_metric': metrics_query.tiflash_storage,
             'query_capacity': capacity_query.tiflash_storage},
        ]

        dataset = []

        for request in requests:
            self.logger.info("{} {}: Retrieving resource usage metrics".format(request['component'], request['name']))
            usage_metrics = client.get_resource_usage_metrics(request)
            self.logger.debug(usage_metrics)
            self.logger.info("{} {}: Retrieving resource capacity".format(request['component'], request['name']))
            capacity, instance_cnt = client.get_capacity_n_count(request)
            analyzer = MetricsAnalyzer(request, usage_metrics, capacity, instance_cnt, self.conf)
            self.logger.info("{} {}: Analyzing capacity plan".format(request['component'], request['name']))
            data = analyzer.analyze()
            if data is not None:
                dataset.append(data)

        return dataset

    def k8s_prom_capacity_plan(self):
        #k8s_prom_url = "https://www.ds.us-east-1.aws.observability.tidbcloud.com/internal/metrics/d5d1a915-1d37-22a7-82b8-8cb67cc57820"

        # require office network, no authentication needed
        client = PrometheusClient(self.conf, 'k8s', False)

        k8s_instance_query = K8sPromQueryInstance(self.conf['cluster_info'])

        k8s_prom_instance_request = [
            {'component': 'tidb', 'query': k8s_instance_query.tidb_instance_query},
            {'component': 'tikv', 'query': k8s_instance_query.tikv_instance_query},
            {'component': 'pdb', 'query': k8s_instance_query.pd_instance_query},
            {'component': 'tiflash', 'query': k8s_instance_query.tiflash_instance_query},
        ]

        dataset = []

        for request in k8s_prom_instance_request:
            self.logger.info("Retrieving {} instances information".format(request['component']))
            self.logger.debug("query: {}".format(request['query']))
            instances_info = client.get_metrics(request['query'])
            #instances_info = client.get_vector_metrics_many(request['query'])
            self.logger.debug("instance_info {}".format(instances_info))

            instances = []
            instance_type_list = []

            if len(instances_info) > 0:
                for instance in instances_info:
                    instance_name = instance['metric']['label_kubernetes_io_hostname']
                    instance_type = instance['metric']['label_node_kubernetes_io_instance_type']
                    self.logger.debug("instance name:{}, instance_type: {}".format(instance_name, instance_type))
                    instances.append(instance_name)
                    instance_type_list.append(instance_type)

                instance_filter = '|'.join(instances)
                self.logger.debug("instance_filter {}".format(instance_filter))

                metricx_query = K8sPromQueryBatchInstanceMetrics(self.conf['cluster_info'], instance_filter)

                k8s_component_metricx_requests = [
                    {'component': request['component'], 'name': "Disk IOPS", 'query_metric': metricx_query.batch_instance_disk_iops_query },
                    {'component': request['component'], 'name': "Disk Bandwidth(byte)", 'query_metric': metricx_query.batch_instance_disk_bandwidth_query},
                    {'component': request['component'], 'name': "NetworkIn Bandwidth(byte)", 'query_metric': metricx_query.batch_instance_network_received_query},
                    {'component': request['component'], 'name': "NetworkOut Bandwidth(byte)", 'query_metric': metricx_query.batch_instance_network_transmitted_query},
                ]

                for metrics_request in k8s_component_metricx_requests:
                    self.logger.info("{} {}: Retrieving  metrics".format(metrics_request['component'], metrics_request['name']))
                    usage_metrics = client.get_resource_usage_metrics(metrics_request)
                    self.logger.info("{} {}: Retrieving capacity".format(metrics_request['component'], metrics_request['name']))
                    instance_cnt = len(instances)
                    instance_type = instance_type_list[0]
                    name = metrics_request['name']
                    capacity = ec2_resource_capacity[instance_type][name]
                    self.logger.info("{} {}: Analyzing capacity plan".format(metrics_request['component'], metrics_request['name']))
                    analyzer = MetricsAnalyzer(metrics_request, usage_metrics, capacity, instance_cnt, self.conf)
                    data = analyzer.analyze()
                    if data is not None:
                        dataset.append(data)

        return dataset

    def generate_capacity_plan(self, mode):
        plan = []
        if mode == "cluster":
            plan = self.cluster_prom_capacity_plan()
        elif mode == "node":
            plan = self.k8s_prom_capacity_plan()
        elif mode == "all":
            plan = self.cluster_prom_capacity_plan() + self.k8s_prom_capacity_plan()
        else:
            self.logger.error("Not supported mode: {}!".format(mode))
            sys.exit(1)

        if len(plan) > 0:
            helpers.write_to_csv(plan, self.csv_file_fields, self.csv_file_name)
            self.logger.info("Completed. Please find the capacity plan in {}".format(self.csv_file_name))
        else:
            self.logger.info("No capacity plan generated.")
