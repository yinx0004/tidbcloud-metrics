from prometheus_api_client import PrometheusConnect
from datetime import datetime
import sys
import csv


# User Input Area
# Define start and end time dd-mm-YYYY HH:MM:SS

start_time = '06/02/2024 00:00:00'
end_time = '07/02/2024 23:59:59'

# Prometheus datapoint interval
step_in_seconds = 60

# Auth

id_token = "xxxxxxxx-xxxx-xxxx"
cluster_prom_base_url = "https://"

# capacity plan variables

plan_traffic_x = 2
plan_resource_redundancy_x = 2

# User Input Area Ends here.

now = datetime.now()
date_time = now.strftime("%Y-%m-%d-%H-%M-%S")

cluster_id = cluster_prom_base_url.split("/")[-1]

csv_file_name = "{}_capacity_plan_{}.csv".format(cluster_id, date_time)

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


def convert_datetime(datetime_str):
    datetime_object = datetime.strptime(datetime_str, '%d/%m/%Y %H:%M:%S')
    return datetime_object


def connect_to_prometheus():
    prom = PrometheusConnect(url=cluster_prom_base_url, disable_ssl=False,
                             headers={"Authorization": "bearer {}".format(id_token)})

    if len(prom.all_metrics()) == 0:
        print("Connect to prometheus failed.")
        sys.exit(0)
    else:
        return prom


def get_metrics(prom, request, step=step_in_seconds):
    if 'step' in request.keys():
        step = request['step']
    res = prom.get_metric_aggregation(
        query=request['query_metric'],
        start_time=start_time_datetime, end_time=end_time_datetime, step=step, operations=["max", "average", "percentile_50", "percentile_75", "percentile_80", "percentile_85", "percentile_90", "percentile_95", "percentile_99", "percentile_99.9"])
    return res


def get_capacity_n_count(prom, request):
    res = prom.custom_query(request['query_capacity'])
    if res is not None:
        instance_cnt = len(res)
        value = res[0]['value']
        capacity = value[1]
        return capacity, instance_cnt
    else:
        return None, None


def get_capacity_plan(aggregations, plan_traffic_x, plan_resource_redundancy_x, instance_cnt, capacity):
    plan = {}
    for k, v in aggregations.items():
        key = "plan_{}".format(k)
        plan[key] = plan_traffic_x * plan_resource_redundancy_x * v.item() * instance_cnt / int(capacity)
    return plan


def write_to_csv(dict_var, file_name):
    fields = ['component', 'name', 'max', 'average', 'percentile_50.0', 'percentile_75.0', "percentile_80.0", "percentile_85.0", "percentile_90.0", "percentile_95.0", 'percentile_99.0', 'percentile_99.9', 'capacity', 'instance_cnt', 'plan_max', 'plan_average', 'plan_percentile_50.0', 'plan_percentile_75.0', 'plan_percentile_80.0', 'plan_percentile_85.0', 'plan_percentile_90.0', 'plan_percentile_95.0', 'plan_percentile_99.0', 'plan_percentile_99.9']
    with open(file_name, "w") as f:
        w = csv.DictWriter(f, fields)
        w.writeheader()
        w.writerows(dict_var)


if __name__ == '__main__':
    prom = connect_to_prometheus()
    metrics = []

    # Convert time to datetime

    start_time_datetime = convert_datetime(start_time)
    end_time_datetime = convert_datetime(end_time)

    # Get metrics, capacity, number of instance for each component

    for request in requests:
        print("{} {}:".format(request['component'], request['name']))
        print("  Retrieving metrics")
        values = get_metrics(prom, request)
        if values is not None:
            metric = {"component": "{}".format(request['component']),
                     "name": "{}".format(request['name']),
                     "max": "{}".format(values['max']), "average": "{}".format(values['average']),
                     "percentile_50.0": "{}".format(values['percentile_50.0']),
                     "percentile_75.0": "{}".format(values['percentile_75.0']),
                     "percentile_80.0": "{}".format(values['percentile_80.0']),
                     "percentile_85.0": "{}".format(values['percentile_85.0']),
                     "percentile_90.0": "{}".format(values['percentile_90.0']),
                     "percentile_95.0": "{}".format(values['percentile_95.0']),
                     "percentile_99.0": "{}".format(values['percentile_99.0']),
                     "percentile_99.9": "{}".format(values['percentile_99.9']), }

            print("  Retrieving capacity and instance count")
            capacity, instance_cnt = get_capacity_n_count(prom, request)
            metric['capacity'] = capacity
            metric['instance_cnt'] = instance_cnt

            print("  Generating capacity plan")
            plan = get_capacity_plan(values, plan_traffic_x, plan_resource_redundancy_x, instance_cnt, capacity)
            for k, v in plan.items():
                metric[k] = v

            metrics.append(metric)
            print("  Done.")

    # Output to csv file

    write_to_csv(metrics, csv_file_name)
    print("\nCompleted. Please find the metrics in {}".format(csv_file_name))
