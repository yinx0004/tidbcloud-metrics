from datetime import datetime
from utils import logger, helpers
from utils.configer import Configer
from prometheus.prometheus_client import PrometheusClient
from capacity_planner.metrics_analyzer import MetricsAnalyzer
from capacity_planner.aws_ec2_capacity import ec2_resource_capacity
from prometheus.k8s_prom_query import K8sPromQueryInstance, K8sPromQueryBatchInstanceMetrics


def cluster_prom_capacity_plan():
    client = PrometheusClient(conf['prometheus_cluster_prom_base_url'], conf['prometheus_start_time'],
                              conf['prometheus_end_time'], conf['prometheus_step_in_seconds'], conf['log_file_name'],
                              conf['log_level'], conf['prometheus_cluster_prom_id_token'])

    # Add 'step' key for customized interval
    cloud_prom_requests = [
        {'component': 'tidb', 'name': "CPU(core)",
         'query_metric': 'irate(process_cpu_seconds_total{component="tidb"}[2m])',
         'query_capacity': 'count(node_cpu_seconds_total{mode="user", instance=~"db-tidb-.*"}) by (instance)',
         'step': '30s'},
        {'component': 'tidb', 'name': "Memory(byte)", 'query_metric': 'process_resident_memory_bytes{component="tidb"}',
         'query_capacity': 'node_memory_MemTotal_bytes{component="tidb"}'},
        {'component': 'tikv', 'name': "CPU(core)",
         'query_metric': 'sum(rate(process_cpu_seconds_total{component=~".*tikv"}[2m])) by (instance)',
         'query_capacity': 'count(node_cpu_seconds_total{mode="user", instance=~"db-tikv-.*"}) by (instance)',
         'step': '30s'},
        {'component': 'tikv', 'name': "Memory(byte)",
         'query_metric': 'avg(process_resident_memory_bytes{component=~".*tikv"}) by (instance)',
         'query_capacity': 'node_memory_MemTotal_bytes{component="tikv"}'},
        {'component': 'tikv', 'name': "Storage(byte)",
         'query_metric': 'sum(tikv_store_size_bytes{type="used"}) by (instance)',
         'query_capacity': 'sum(tikv_store_size_bytes{type="capacity"}) by (instance)'},
        {'component': 'pd', 'name': "CPU(core)",
         'query_metric': 'irate(process_cpu_seconds_total{component=~".*pd.*"}[2m])',
         'query_capacity': 'count(node_cpu_seconds_total{mode="user", instance=~"db-pd-.*"}) by (instance)',
         'step': '2m'},
        {'component': 'pd', 'name': "Memory(byte)",
         'query_metric': 'process_resident_memory_bytes{component=~".*pd.*"}',
         'query_capacity': 'node_memory_MemTotal_bytes{component="pd"}', 'step': '2m'},
        {'component': 'tiflash', 'name': "CPU(core)",
         'query_metric': 'rate(tiflash_proxy_process_cpu_seconds_total{component="tiflash"}[2m])',
         'query_capacity': 'count(node_cpu_seconds_total{mode="user", instance=~"db-tiflash-.*"}) by (instance)'},
        {'component': 'tiflash', 'name': "Memory(byte)",
         'query_metric': 'tiflash_proxy_process_resident_memory_bytes{component="tiflash"}',
         'query_capacity': 'node_memory_MemTotal_bytes{component="tiflash"}'},
        {'component': 'tiflash', 'name': "Storage(byte)",
         'query_metric': 'sum(tiflash_system_current_metric_StoreSizeUsed) by (instance)',
         'query_capacity': 'sum(tiflash_system_current_metric_StoreSizeCapacity) by (instance)'},
    ]

    dataset = []

    for request in cloud_prom_requests:
        logger.info("{} {}: Retrieving resource usage metrics".format(request['component'], request['name']))
        usage_metrics = client.get_resource_usage_metrics(request)
        logger.debug(usage_metrics)
        logger.info("{} {}: Retrieving resource capacity".format(request['component'], request['name']))
        capacity, instance_cnt = client.get_capacity_n_count(request)
        analyzer = MetricsAnalyzer(request, usage_metrics, capacity, instance_cnt, conf['capacity_plan_traffic_x'],
                                   conf['capacity_plan_resource_redundancy_x'], conf['log_file_name'], conf['log_level'])
        logger.info("{} {}: Analyzing capacity plan".format(request['component'], request['name']))
        data = analyzer.analyze()
        if data is not None:
            dataset.append(data)

    return dataset


def k8s_prom_capacity_plan(cluster_info):
    k8s_prom_region_url = "https://www.ds.us-east-1.aws.observability.tidbcloud.com/internal/metrics/d5d1a915-1d37-22a7-82b8-8cb67cc57820"

    # require office network, no authentication needed
    client = PrometheusClient(k8s_prom_region_url, conf['prometheus_start_time'], conf['prometheus_end_time'], conf['prometheus_step_in_seconds'], conf['log_file_name'], conf['log_level'])

    k8s_instance_query = K8sPromQueryInstance(cluster_info)

    k8s_prom_instance_request = [
        {'component': 'tidb', 'query': k8s_instance_query.tidb_instance_query},
        {'component': 'tikv', 'query': k8s_instance_query.tikv_instance_query},
        {'component': 'pdb', 'query': k8s_instance_query.pd_instance_query},
        {'component': 'tiflash', 'query': k8s_instance_query.tiflash_instance_query},
    ]

    dataset = []

    for request in k8s_prom_instance_request:
        logger.info("Retrieving {} instances information".format(request['component']))
        logger.debug("query: {}".format(request['query']))
        instances_info = client.get_metrics(request['query'])
        logger.debug("instance_info {}".format(instances_info))

        instances = []
        instance_type_list = []

        if len(instances_info) > 0:
            for instance in instances_info:
                instance_name = instance['metric']['label_kubernetes_io_hostname']
                instance_type = instance['metric']['label_node_kubernetes_io_instance_type']
                logger.debug("instance name:{}, instance_type: {}".format(instance_name, instance_type))
                instances.append(instance_name)
                instance_type_list.append(instance_type)

            instance_filter = '|'.join(instances)
            logger.debug("instance_filter {}".format(instance_filter))

            k8s_component_metricx_query = K8sPromQueryBatchInstanceMetrics(cluster_info, instance_filter)

            k8s_component_metricx_requests = [
                {'component': request['component'], 'name': "Disk IOPS", 'query_metric': k8s_component_metricx_query.batch_instance_disk_iops_query },
                {'component': request['component'], 'name': "Disk Bandwidth(byte)", 'query_metric': k8s_component_metricx_query.batch_instance_disk_bandwidth_query},
                {'component': request['component'], 'name': "NetworkIn Bandwidth(byte)", 'query_metric': k8s_component_metricx_query.batch_instance_network_received_query},
                {'component': request['component'], 'name': "NetworkOut Bandwidth(byte)", 'query_metric': k8s_component_metricx_query.batch_instance_network_transmitted_query},
            ]

            for metrics_request in k8s_component_metricx_requests:
                logger.info("{} {}: Retrieving  metrics".format(metrics_request['component'], metrics_request['name']))
                usage_metrics = client.get_resource_usage_metrics(metrics_request)
                logger.info("{} {}: Retrieving capacity".format(metrics_request['component'], metrics_request['name']))
                instance_cnt = len(instances)
                instance_type = instance_type_list[0]
                name = metrics_request['name']
                capacity = ec2_resource_capacity[instance_type][name]
                logger.info("{} {}: Analyzing capacity plan".format(metrics_request['component'], metrics_request['name']))
                analyzer = MetricsAnalyzer(metrics_request, usage_metrics, capacity, instance_cnt, conf['capacity_plan_traffic_x'],
                                           conf['capacity_plan_resource_redundancy_x'], conf['log_file_name'],
                                           conf['log_level'])
                data = analyzer.analyze()
                if data is not None:
                    dataset.append(data)

    return dataset


def get_tidb_cluster_info(prometheus_cluster_prom_base_url):
    info = prometheus_cluster_prom_base_url.split("/")
    cluster_info = {
        'ds_domain': info[2],
        'tenant_id': info[7],
        'project_id': info[9],
        'cluster_id': info[-1],
    }
    domain_info = cluster_info['ds_domain'].split('.')
    cluster_info['region'] = domain_info[2]
    cluster_info['cloud_provider'] = domain_info[3]
    cluster_info['k8s_cluster'] = 'prod-{}-eks-{}-.*'.format(cluster_info['project_id'], cluster_info['region'])

    return cluster_info


if __name__ == '__main__':
    now = datetime.now()
    date_time_str = now.strftime("%Y-%m-%d-%H-%M-%S")

    # get configurations
    conf = Configer("tidbcloud.yaml", now).set_conf()

    cluster_info = get_tidb_cluster_info(conf['prometheus_cluster_prom_base_url'])
    csv_file_name = "data/{}_capacity_plan_{}.csv".format(cluster_info['cluster_id'], date_time_str)
    csv_fields = ['component', 'name', 'max', 'average', 'percentile_50.0', 'percentile_75.0', "percentile_80.0",
                  "percentile_85.0", "percentile_90.0", "percentile_95.0", 'percentile_99.0', 'percentile_99.9',
                  'capacity', 'instance_cnt', 'plan_max', 'plan_average', 'plan_percentile_50.0',
                  'plan_percentile_75.0', 'plan_percentile_80.0', 'plan_percentile_85.0', 'plan_percentile_90.0',
                  'plan_percentile_95.0', 'plan_percentile_99.0', 'plan_percentile_99.9']

    # setup logging
    if conf['log_to_file']:
        conf['log_file_name'] = "logs/{}_{}.log".format(cluster_info['cluster_id'], date_time_str)

    logger = logger.setup_logger(__name__, conf['log_file_name'], conf['log_level'])
    logger.debug("test")

    dataset_cluster_prom = cluster_prom_capacity_plan()
    logger.debug("dataset_cluster_prom: {}".format(dataset_cluster_prom))
    dataset_k8s_prom = k8s_prom_capacity_plan(cluster_info)
    logger.debug("dataset_k8s_prom: {}".format(dataset_k8s_prom))
    dataset = dataset_cluster_prom + dataset_k8s_prom
    logger.debug("dataset: {}".format(dataset))

    helpers.write_to_csv(dataset, csv_fields, csv_file_name)
    logger.info("Completed. Please find the capacity plan in {}".format(csv_file_name))


