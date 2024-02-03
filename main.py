from prometheus_api_client import PrometheusConnect
from datetime import datetime
import sys
import csv


# User Input Area
# Define start and end time DD-MM-YYYY HH:MM:SS

start_time = '01/02/2024 00:00:00'
end_time = '02/02/2024 23:59:59'

# Auth

id_token = "xxxxxxxx-xxxx-xxxx"
cluster_prom_base_url = "https://"

# User Input Area Ends here.


csv_file_name = "metrics.csv"

request_list = [
    {'component': 'tidb', 'name': "Max CPU", 'query': 'irate(process_cpu_seconds_total{component="tidb"}[2m])', 'step': '15s'},
    {'component': 'tidb', 'name': "Max Memory", 'query': 'process_resident_memory_bytes{component="tidb"}', 'step': '15s'},
    {'component': 'tikv', 'name': "Max CPU", 'query': 'sum(rate(process_cpu_seconds_total{component=~".*tikv"}[2m])) by (instance)', 'step': '15s'},
    {'component': 'tikv', 'name': "Max Memory", 'query': 'avg(process_resident_memory_bytes{component=~".*tikv"}) by (instance)', 'step': '15s'},
    {'component': 'tikv', 'name': "Max Storage", 'query': 'sum(tikv_store_size_bytes{type="used"}) by (instance)', 'step': '15s'},
    {'component': 'pd', 'name': "Max CPU", 'query': 'irate(process_cpu_seconds_total{component=~".*pd.*"}[2m])', 'step': '2m'},
    {'component': 'pd', 'name': "Max Memory", 'query': 'process_resident_memory_bytes{component=~".*pd.*"}', 'step': '2m'},
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


def get_max(prom, request):
    res_max = prom.get_metric_aggregation(
        query=request['query'],
        start_time=start_time_datetime, end_time=end_time_datetime, step=request['step'], operations=["max"])
    return res_max['max']


def dict_to_csv(dict_var, file_name):
    fields = ['component', 'name', 'value']
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
        value = get_max(prom, request)
        metrics.append({"component": "{}".format(request['component']), "name": "{}".format(request['name']), "value": "{}".format(value)})

    # Output to csv file

    dict_to_csv(metrics, csv_file_name)
