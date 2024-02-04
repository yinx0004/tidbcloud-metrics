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
- `start_time`: Prometheus query start time, format: 'DD-MM-YYYY HH:MM:SS'
- `end_time`: Prometheus query ent time, format:'DD-MM-YYYY HH:MM:SS'
- `step_in_seconds`: Prometheus query step(interval), unit is second, normally 60 for two days, 30 for 1 day
- `id_token`: Token for prometheus API
- `cluster_prom_base_url`: URL for prometheus API, contains TiDBCloud Cluster information
2. How to get `id_token` and `cluster_prom_base_url`
- step 1, login tidbcloud.com in Chrome
- step 2, right-click the page to `Inspect`
- step 3, goto `Application` tab, 
- step 4, under `Local storage` -> https://tidbcloud.com



