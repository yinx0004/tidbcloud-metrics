class CloudPromComponentMetricsQuery(object):
    def __init__(self, access_point_id=None):
        self.tidb_uptime = '(time() - process_start_time_seconds{component="tidb"})'
        self.tidb_cpu = 'irate(process_cpu_seconds_total{component="tidb"}[2m])'
        self.tidb_cpu_ac = 'irate(process_cpu_seconds_total{component="tidb", instance=~".*-ac-%s"}[2m])' % access_point_id
        self.tidb_cpu_ac_default = 'irate(process_cpu_seconds_total{component="tidb", instance!~".*-ac-.*"}[2m])'
        self.tidb_memory = 'process_resident_memory_bytes{component="tidb"}'
        self.tidb_memory_ac = 'process_resident_memory_bytes{component="tidb", instance=~".*-ac-%s"}' % access_point_id
        self.tidb_memory_ac_default = 'process_resident_memory_bytes{component="tidb", instance!~".*-ac-.*"}'
        self.tikv_cpu = 'sum(rate(process_cpu_seconds_total{component=~".*tikv"}[2m])) by (instance)'
        self.tikv_memory = 'avg(process_resident_memory_bytes{component=~".*tikv"}) by (instance)'
        self.tikv_storage = 'sum(tikv_store_size_bytes{type="used"}) by (instance)'
        self.pd_cpu = 'irate(process_cpu_seconds_total{component=~".*pd.*"}[2m])'
        self.pd_memory = 'process_resident_memory_bytes{component=~".*pd.*"}'
        self.tiflash_cpu = 'rate(tiflash_proxy_process_cpu_seconds_total{component="tiflash"}[2m])'
        self.tiflash_memory = 'tiflash_proxy_process_resident_memory_bytes{component="tiflash"}'
        self.tiflash_storage = 'sum(tiflash_system_current_metric_StoreSizeUsed) by (instance)'


class CloudPromComponentCapacityQuery(object):
    def __init__(self, access_point_id=None):
        self.tidb_cpu = 'count(node_cpu_seconds_total{mode="user", instance=~"db-tidb-.*"}) by (instance)'
        self.tidb_cpu_ac = 'count(node_cpu_seconds_total{mode="user", instance=~"db-tidb-.*-ac-%s"}) by (instance)' % access_point_id
        self.tidb_cpu_ac_default = 'count(node_cpu_seconds_total{mode="user", instance=~"db-tidb-[0-9]+"}) by (instance)'
        self.tidb_memory = 'node_memory_MemTotal_bytes{component="tidb"}'
        self.tidb_memory_ac = 'node_memory_MemTotal_bytes{component="tidb", instance=~".*-ac-%s"}' % access_point_id
        self.tidb_memory_ac_default = 'node_memory_MemTotal_bytes{component="tidb", instance!~".*-ac-.*"}'
        self.tikv_cpu = 'count(node_cpu_seconds_total{mode="user", instance=~"db-tikv-.*"}) by (instance)'
        self.tikv_memory = 'node_memory_MemTotal_bytes{component="tikv"}'
        self.tikv_storage = 'sum(tikv_store_size_bytes{type="capacity"}) by (instance)'
        self.pd_cpu = 'count(node_cpu_seconds_total{mode="user", instance=~"db-pd-.*"}) by (instance)'
        self.pd_memory = 'node_memory_MemTotal_bytes{component="pd"}'
        self.tiflash_cpu = 'count(node_cpu_seconds_total{mode="user", instance=~"db-tiflash-.*"}) by (instance)'
        self.tiflash_memory = 'node_memory_MemTotal_bytes{component="tiflash"}'
        self.tiflash_storage = 'sum(tiflash_system_current_metric_StoreSizeCapacity) by (instance)'


health_query = {
    'tidb': {
        'query_duration_p999': 'histogram_quantile(0.999, sum(rate(tidb_server_handle_query_duration_seconds_bucket[2m])) by (le))',
        'qps': 'sum(rate(tidb_executor_statement_total[2m]))',
        'failed_query_opm': 'sum(increase(tidb_server_execute_error_total[1m])) by (type, instance)',
        'data_size': 'sum(pd_cluster_status{type="storage_size"})'
        #'last_gc_time':'',
    },
    'tikv': {
        'miss_peer_region_count': 'pd_regions_status{type="miss-peer-region-count"}',
        'extra_peer_region_count': 'pd_regions_status{type="extra-peer-region-count"}',
        'empty_region_count': 'pd_regions_status{type="empty-region-count"}',
        'pending_peer_region_count': 'pd_regions_status{type="pending-peer-region-count"}',
        'down_peer_region_count': 'pd_regions_status{type="down-peer-region-count"}',
        'offline_peer_region_count': 'pd_regions_offline_status{type="offline-peer-region-count"}',
        #'kv_request_duration_99_by_store': 'max(histogram_quantile(0.99, sum(rate(tidb_tikvclient_request_seconds_bucket{store!="0"}[2m])) by (le, store)))',
        'region_count': 'max(sum(tikv_raftstore_region_count{type="region"}) by (instance))',
        'tikv_engine_write_stall': 'max(avg(tikv_engine_write_stall{type="write_stall_percentile99"}) by (instance, db))',
        'tikv_scheduler_too_busy_total': 'max(sum(rate(tikv_scheduler_too_busy_total[2m])) by (instance))',
        'tikv_channel_full_total': 'max(sum(rate(tikv_channel_full_total[2m])) by (instance, type))',
        'tikv_coprocessor_request_error': 'max(sum(rate(tikv_coprocessor_request_error{type="full"}[2m])) by (instance))',
        'tikv_raftstore_store_write_msg_block_wait_duration_seconds_count': 'max(sum(rate(tikv_raftstore_store_write_msg_block_wait_duration_seconds_count[2m])) by (instance))',
        'tikv_grpc_msg_duration_999': 'max(histogram_quantile(0.99, sum(rate(tikv_grpc_msg_duration_seconds_bucket{type!="kv_gc"}[2m])) by (le, type)))',
    },
    'pd': {
        'pd_tso_wait_duration_999': 'histogram_quantile(0.999, sum(rate(pd_client_cmd_handle_cmds_duration_seconds_bucket{type="wait"}[2m])) by (le))',
        'store_disconnected_count': 'sum(pd_cluster_status{type="store_disconnected_count"})',
        'store_unhealth_count': 'sum(pd_cluster_status{type="store_unhealth_count"})',
        'store_low_space_count': 'sum(pd_cluster_status{type="store_low_space_count"})',
        'store_down_count': 'sum(pd_cluster_status{type="store_down_count"})',
        'store_offline_count': 'sum(pd_cluster_status{type="store_offline_count"})',
        'store_tombstone_count': 'sum(pd_cluster_status{type="store_tombstone_count"})',
        'store_slow_count': 'sum(pd_cluster_status{type="store_slow_count"})',
    },
    'tiflash': {
        'request_duration_p999': 'histogram_quantile(0.999, sum(rate(tiflash_coprocessor_request_duration_seconds_bucket[2m])) by (le))',
        'tiflash_raft_wait_index_duration_max': 'histogram_quantile(1.00, sum(rate(tiflash_raft_wait_index_duration_seconds_bucket[2m])) by (le))',
        'tiflash_raft_read_index_duration_max': 'histogram_quantile(1.00, sum(rate(tiflash_raft_read_index_duration_seconds_bucket[2m])) by (le))',
    },
    'cluster': {},
}

config_query = {
    'gc': '',
}

component_query = 'count(node_memory_MemTotal_bytes) by (component)'
