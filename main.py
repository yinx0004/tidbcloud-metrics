from datetime import datetime
from utils import logger, helpers
from utils.configer import Configer
from capacity_planner.prometheus_client import PrometheusClient
from capacity_planner.metrics_analyzer import MetricsAnalyzer


# consts
csv_fields = ['component', 'name', 'max', 'average', 'percentile_50.0', 'percentile_75.0', "percentile_80.0", "percentile_85.0", "percentile_90.0", "percentile_95.0", 'percentile_99.0', 'percentile_99.9', 'capacity', 'instance_cnt', 'plan_max', 'plan_average', 'plan_percentile_50.0', 'plan_percentile_75.0', 'plan_percentile_80.0', 'plan_percentile_85.0', 'plan_percentile_90.0', 'plan_percentile_95.0', 'plan_percentile_99.0', 'plan_percentile_99.9']

# Add 'step' key for customized interval
requests = [
    {'component': 'tidb', 'name': "CPU(core)", 'query_metric': 'irate(process_cpu_seconds_total{component="tidb"}[2m])', 'query_capacity': 'count(node_cpu_seconds_total{mode="user", instance=~"db-tidb-.*"}) by (instance)', 'step': '30s'},
    {'component': 'tidb', 'name': "Memory(byte)", 'query_metric': 'process_resident_memory_bytes{component="tidb"}', 'query_capacity': 'node_memory_MemTotal_bytes{component="tidb"}'},
    {'component': 'tikv', 'name': "CPU(core)", 'query_metric': 'sum(rate(process_cpu_seconds_total{component=~".*tikv"}[2m])) by (instance)', 'query_capacity': 'count(node_cpu_seconds_total{mode="user", instance=~"db-tikv-.*"}) by (instance)', 'step': '30s'},
    {'component': 'tikv', 'name': "Memory(byte)", 'query_metric': 'avg(process_resident_memory_bytes{component=~".*tikv"}) by (instance)', 'query_capacity': 'node_memory_MemTotal_bytes{component="tikv"}'},
    {'component': 'tikv', 'name': "Storage(byte)", 'query_metric': 'sum(tikv_store_size_bytes{type="used"}) by (instance)', 'query_capacity': 'sum(tikv_store_size_bytes{type="capacity"}) by (instance)'},
    {'component': 'pd', 'name': "CPU(core)", 'query_metric': 'irate(process_cpu_seconds_total{component=~".*pd.*"}[2m])', 'query_capacity': 'count(node_cpu_seconds_total{mode="user", instance=~"db-pd-.*"}) by (instance)', 'step': '2m'},
    {'component': 'pd', 'name': "Memory(byte)", 'query_metric': 'process_resident_memory_bytes{component=~".*pd.*"}', 'query_capacity': 'node_memory_MemTotal_bytes{component="pd"}', 'step': '2m'},
    {'component': 'tiflash', 'name': "CPU(core)", 'query_metric': 'rate(tiflash_proxy_process_cpu_seconds_total{component="tiflash"}[2m])', 'query_capacity': 'count(node_cpu_seconds_total{mode="user", instance=~"db-tiflash-.*"}) by (instance)'},
    {'component': 'tiflash', 'name': "Memory(byte)", 'query_metric': 'tiflash_proxy_process_resident_memory_bytes{component="tiflash"}', 'query_capacity': 'node_memory_MemTotal_bytes{component="tiflash"}'},
    {'component': 'tiflash', 'name': "Storage(byte)", 'query_metric': 'sum(tiflash_system_current_metric_StoreSizeUsed) by (instance)', 'query_capacity': 'sum(tiflash_system_current_metric_StoreSizeCapacity) by (instance)'},
]


def get_capacity_plan(aggregations, plan_traffic_x, plan_resource_redundancy_x, instance_cnt, capacity):
    plan = {}
    for k, v in aggregations.items():
        key = "plan_{}".format(k)
        plan[key] = plan_traffic_x * plan_resource_redundancy_x * v.item() * instance_cnt / int(capacity)
    return plan


if __name__ == '__main__':
    now = datetime.now()
    date_time_str = now.strftime("%Y-%m-%d-%H-%M-%S")

    # get configurations
    conf = Configer("tidbcloud.yaml", now).set_conf()

    cluster_id = conf['prometheus_cluster_prom_base_url'].split("/")[-1]

    csv_file_name = "data/{}_capacity_plan_{}.csv".format(cluster_id, date_time_str)

    # setup logging
    if conf['log_to_file']:
        conf['log_file_name'] = "logs/{}_{}.log".format(cluster_id, date_time_str)

    logger = logger.setup_logger(__name__, conf['log_file_name'], conf['log_level'])
    logger.debug("test")

    client = PrometheusClient(conf['prometheus_cluster_prom_base_url'], conf['prometheus_cluster_prom_id_token'], conf['prometheus_start_time'], conf['prometheus_end_time'], conf['prometheus_step_in_seconds'], conf['log_file_name'], conf['log_level'])

    dataset = []

    for request in requests:
        logger.info("{} {}: Retrieving resource usage metrics".format(request['component'], request['name']))
        usage_metrics = client.get_resource_usage_metrics(request)
        logger.info("{} {}: Retrieving resource capacity".format(request['component'], request['name']))
        capacity_metrics = client.get_resource_capacity_metrics(request)
        analyzer = MetricsAnalyzer(request, usage_metrics, capacity_metrics, conf['capacity_plan_traffic_x'], conf['capacity_plan_resource_redundancy_x'], conf['log_file_name'], conf['log_level'])
        logger.info("{} {}: Analyzing capacity plan".format(request['component'], request['name']))
        data = analyzer.analyze()
        dataset.append(data)

    helpers.write_to_csv(dataset, csv_fields, csv_file_name)
    logger.info("Completed. Please find the capacity plan in {}".format(csv_file_name))
