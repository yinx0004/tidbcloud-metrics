from prometheus_api_client import PrometheusConnect
from datetime import datetime
import sys
import csv


# User Input Area
# Define start and end time dd-mm-YYYY HH:MM:SS

start_time = '01/02/2024 00:00:00'
end_time = '02/02/2024 23:59:59'

# Prometheus datapoint interval
step_in_seconds = 60

# Auth

id_token = "xxxxxxxx-xxxx-xxxx"
cluster_prom_base_url = "https://"


# User Input Area Ends here.


csv_file_name = "metrics.csv"

# Add 'step' key for customized interval
request_list = [
    {'component': 'tidb', 'name': "CPU(core)", 'query': 'irate(process_cpu_seconds_total{component="tidb"}[2m])', 'step': '30s'},
    {'component': 'tidb', 'name': "Memory(byte)", 'query': 'process_resident_memory_bytes{component="tidb"}'},
    {'component': 'tikv', 'name': "CPU(core)", 'query': 'sum(rate(process_cpu_seconds_total{component=~".*tikv"}[2m])) by (instance)'},
    {'component': 'tikv', 'name': "Memory(byte)", 'query': 'avg(process_resident_memory_bytes{component=~".*tikv"}) by (instance)'},
    {'component': 'tikv', 'name': "Storage(byte)", 'query': 'sum(tikv_store_size_bytes{type="used"}) by (instance)'},
    {'component': 'pd', 'name': "CPU(core)", 'query': 'irate(process_cpu_seconds_total{component=~".*pd.*"}[2m])', 'step': '2m'},
    {'component': 'pd', 'name': "Memory(byte)", 'query': 'process_resident_memory_bytes{component=~".*pd.*"}', 'step': '2m'},
    {'component': 'tiflash', 'name': "CPU(core)", 'query': 'rate(tiflash_proxy_process_cpu_seconds_total{component="tiflash"}[2m])'},
    {'component': 'tiflash', 'name': "Memory(byte)", 'query': 'tiflash_proxy_process_resident_memory_bytes{component="tiflash"}'},
    {'component': 'tiflash', 'name': "Storage(byte)", 'query': 'sum(tiflash_system_current_metric_StoreSizeUsed) by (instance)'},
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
        query=request['query'],
        start_time=start_time_datetime, end_time=end_time_datetime, step=step, operations=["max", "average", "percentile_50", "percentile_75", "percentile_99", "percentile_99.9"])
    return res


def dict_to_csv(dict_var, file_name):
    fields = ['component', 'name', 'max', 'average', 'percentile_50.0', 'percentile_75.0', 'percentile_99.0', 'percentile_99.9']
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

    # Get Metrics

    for request in request_list:
        values = get_metrics(prom, request)
        if values is not None:
            metrics.append({"component": "{}".format(request['component']), "name": "{}".format(request['name']), "max": "{}".format(values['max']), "average": "{}".format(values['average']), "percentile_50.0": "{}".format(values['percentile_50.0']), "percentile_75.0": "{}".format(values['percentile_75.0']), "percentile_99.0": "{}".format(values['percentile_99.0']), "percentile_99.9": "{}".format(values['percentile_99.9'])})

    # Output to csv file

    dict_to_csv(metrics, csv_file_name)
    print("Please find the metrics in {}".format(csv_file_name))