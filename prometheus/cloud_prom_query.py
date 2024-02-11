class CloudPromComponentMetricsQuery(object):
    def __init__(self):
        self.tidb_cpu = 'irate(process_cpu_seconds_total{component="tidb"}[2m])'
        self.tidb_memory = 'process_resident_memory_bytes{component="tidb"}'
        self.tikv_cpu = 'sum(rate(process_cpu_seconds_total{component=~".*tikv"}[2m])) by (instance)'
        self.tikv_memory = 'avg(process_resident_memory_bytes{component=~".*tikv"}) by (instance)'
        self.tikv_storage = 'sum(tikv_store_size_bytes{type="used"}) by (instance)'
        self.pd_cpu = 'irate(process_cpu_seconds_total{component=~".*pd.*"}[2m])'
        self.pd_memory = 'process_resident_memory_bytes{component=~".*pd.*"}'
        self.tiflash_cpu = 'rate(tiflash_proxy_process_cpu_seconds_total{component="tiflash"}[2m])'
        self.tiflash_memory = 'tiflash_proxy_process_resident_memory_bytes{component="tiflash"}'
        self.tiflash_storage = 'sum(tiflash_system_current_metric_StoreSizeUsed) by (instance)'


class CloudPromComponentCapacityQuery(object):
    def __init__(self):
        self.tidb_cpu = 'count(node_cpu_seconds_total{mode="user", instance=~"db-tidb-.*"}) by (instance)'
        self.tidb_memory = 'node_memory_MemTotal_bytes{component="tidb"}'
        self.tikv_cpu = 'count(node_cpu_seconds_total{mode="user", instance=~"db-tikv-.*"}) by (instance)'
        self.tikv_memeory = 'node_memory_MemTotal_bytes{component="tikv"}'
        self.tikv_storage = 'sum(tikv_store_size_bytes{type="capacity"}) by (instance)'
        self.pd_cpu = 'count(node_cpu_seconds_total{mode="user", instance=~"db-pd-.*"}) by (instance)'
        self.pd_memory = 'node_memory_MemTotal_bytes{component="pd"}'
        self.tiflash_cpu = 'count(node_cpu_seconds_total{mode="user", instance=~"db-tiflash-.*"}) by (instance)'
        self.tiflash_memory = 'node_memory_MemTotal_bytes{component="tiflash"}'
        self.tiflash_storage = 'sum(tiflash_system_current_metric_StoreSizeCapacity) by (instance)'