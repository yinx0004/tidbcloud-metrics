# Function
Run this script to get TiDBCloud Cluster Metrics in form of a csv file.

# Requirement
- Python3
- prometheus_api_client: A Python wrapper for the Prometheus http api and some tools for metrics processing.
```shell
pip install prometheus-api-client
```

# How to use
1. Configuration 
- `start_time`: Prometheus query start time, format: 'dd-mm-YYYY HH:MM:SS'
- `end_time`: Prometheus query ent time, format:'dd-mm-YYYY HH:MM:SS'
- `step_in_seconds`: Prometheus query step(interval), unit is second, normally 60 for two days, 30 for 1 day
- `id_token`: Token for prometheus API
- `cluster_prom_base_url`: URL for prometheus API, contains TiDBCloud Cluster information
2. How to get `id_token` and `cluster_prom_base_url`
- step 1, login tidbcloud.com in Chrome
- step 2, right-click the page to `Inspect`
- step 3, goto `Application` tab, 
- step 4, under `Local storage` -> https://tidbcloud.com


# For On-premise deployment need minor changes
Replace the following two parts
```python
prom = PrometheusConnect(url="http://prometheus_ip:9090", disable_ssl=False, headers=None)
```

```python
request_list = [
    {'component': 'tidb', 'name': "CPU(core)", 'query': 'irate(process_cpu_seconds_total{job="tidb"}[30s])', 'step': '30s'},#
    {'component': 'tidb', 'name': "Memory(byte)", 'query': 'process_resident_memory_bytes{job="tidb"}'},#
    {'component': 'tikv', 'name': "CPU(core)", 'query': 'sum(rate(process_cpu_seconds_total{job=~".*tikv"}[1m])) by (instance)'}, #
    {'component': 'tikv', 'name': "Memory(byte)", 'query': 'avg(process_resident_memory_bytes{job=~".*tikv"}) by (instance)'},#
    {'component': 'tikv', 'name': "Storage(byte)", 'query': 'sum(tikv_store_size_bytes{type="used"}) by (instance)'},#
    {'component': 'pd', 'name': "CPU(core)", 'query': 'irate(process_cpu_seconds_total{job=~".*pd.*"}[30s])', 'step': '2m'},  #
    {'component': 'pd', 'name': "Memory(byte)", 'query': 'process_resident_memory_bytes{job=~".*pd.*"}', 'step': '2m'}, #
    {'component': 'tiflash', 'name': "CPU(core)", 'query': 'rate(tiflash_proxy_process_cpu_seconds_total{job="tiflash"}[1m])'},
    {'component': 'tiflash', 'name': "Memory(byte)", 'query': 'tiflash_proxy_process_resident_memory_bytes{job="tiflash"}'},
    {'component': 'tiflash', 'name': "Storage(byte)", 'query': 'sum(tiflash_system_current_metric_StoreSizeUsed) by (instance)'},
]
```

