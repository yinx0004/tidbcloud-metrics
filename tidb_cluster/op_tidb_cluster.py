from prometheus.prom_class_promotion import PromotionPrometheusConnect
from datetime import datetime

class OpTidbCluster:
    def __init__(self, conf):
        """
        初始化 prometheus client 和相关参数
        """
        self.conf = conf
        self.conf["start_time"]=datetime.strptime(self.conf["start_time"], "%Y-%m-%d %H:%M:%S")
        self.conf["end_time"]=datetime.strptime(self.conf["end_time"], "%Y-%m-%d %H:%M:%S")
        # self.prome_url=self.get_prome_url_from_clinic_api()
        self.tidb_cluster=self.conf["headers"]["X-ClusterID"]
        self.prome_client = self.get_prome_client()
        self.all_instances_cpu_capacity = self.get_all_instances_cpu_capacity()
        self.all_instances_mem_capacity = self.get_all_instances_mem_capacity()
        # self.queries = self.query_list()
    def get_all_tidb_instance(self):
        """
        获取所有 TiDB instances
        :return: list
        """
        data=self.prome_client.custom_query_range_promotion(query="tidb_server_connections{tidb_cluster='%s'}" % self.tidb_cluster,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"])
        instances = [entry['metric']['instance'].split(":")[0] for entry in data]
        return instances
    

    def get_all_tidb_cpu_usage(self):
        """
        获取所有 TiDB cpu usage
        :return: dict
        """
        operations = ["max", "average","percentile_99"]
        data=self.prome_client.get_metric_aggregation_promotion(query="irate(process_cpu_seconds_total{job='tidb',tidb_cluster='%s'}[30s])" % self.tidb_cluster,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"],operations=operations)
        return data
    def get_all_tidb_mem_usage(self):
        """
        获取所有 TiDB mem usage
        :return: dict
        """
        operations = ["max", "average","percentile_99"]
        data=self.prome_client.get_metric_aggregation_promotion(query="process_resident_memory_bytes{job='tidb',tidb_cluster='%s'}" % self.tidb_cluster,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"],operations=operations)
        return data
    def get_all_pd_instance(self):
        """
        获取所有 PD instances
        :return: list
        """
        data=self.prome_client.custom_query_range_promotion(query="process_start_time_seconds{tidb_cluster='%s',job=~'.*pd.*'}" % self.tidb_cluster,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"])
        instances = [entry['metric']['instance'].split(":")[0] for entry in data]
        return instances
    def get_all_pd_cpu_usage(self):
        """
        获取所有 PD cpu usage
        :return: dict
        """
        operations = ["max", "average","percentile_99"]
        data=self.prome_client.get_metric_aggregation_promotion(query="irate(process_cpu_seconds_total{job=~'.*pd.*',tidb_cluster='%s'}[30s])" % self.tidb_cluster,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"],operations=operations)
        return data
    def get_all_pd_mem_usage(self):
        """
        获取所有 PD mem usage
        :return: dict
        """
        operations = ["max", "average","percentile_99"]
        data=self.prome_client.get_metric_aggregation_promotion(query="process_resident_memory_bytes{job=~'.*pd.*',tidb_cluster='%s'}" % self.tidb_cluster,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"],operations=operations)
        return data

    def get_all_instances_cpu_capacity(self):
        """
        获取所有 instances cpu capacity
        :return: list of dicts, 每个 dict 包含 instance 和 cpu_capacity
        """
        data = self.prome_client.custom_query_range_promotion(
            query="count(node_cpu_seconds_total{mode='user',tidb_cluster='%s'}) by (instance)"  % self.tidb_cluster,
            start_time=self.conf["start_time"],
            end_time=self.conf["end_time"],
            step=self.conf["step_in_seconds"]
        )

        all_instances_cpu_capacity = {entry['metric']['instance'].split(":")[0]:entry['values'][0][1] for entry in data}

        # all_instances_cpu_capacity = []
        # for entry in data:
        #     instance = entry['metric']['instance'].split(":")[0]
        #     cpu_capacity = entry['values'][0][1]
        #     all_instances_cpu_capacity.append({'instance': instance, 'cpu_capacity': cpu_capacity})
        
        return all_instances_cpu_capacity
    
    # node_memory_MemTotal_bytes
    def get_all_instances_mem_capacity(self):
        """
        获取所有 instances mem capacity
        :return: list of dicts, 每个 dict 包含 instance 和 mem_capacity
        """
        data = self.prome_client.custom_query_range_promotion(
            query="node_memory_MemTotal_bytes{tidb_cluster='%s'}" % self.tidb_cluster,
            start_time=self.conf["start_time"],
            end_time=self.conf["end_time"],
            step=self.conf["step_in_seconds"]
        )
        
        all_instances_mem_capacity = {entry['metric']['instance'].split(":")[0]:entry['values'][0][1] for entry in data}
        
        return all_instances_mem_capacity

    def get_all_tikv_instance(self):
        """
        获取所有 TiKV instances
        :return: list
        """
        data=self.prome_client.custom_query_range_promotion(query="process_start_time_seconds{job=~'.*tikv',tidb_cluster='%s'}" % self.tidb_cluster,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"])
        instances = [entry['metric']['instance'].split(":")[0] for entry in data]
        return instances 
    def get_all_tikv_cpu_usage(self):
        """
        获取所有 TiKV cpu usage
        :return: dict
        """
        operations = ["max", "average","percentile_99"]
        data=self.prome_client.get_metric_aggregation_promotion(query="sum(rate(process_cpu_seconds_total{job=~'.*tikv',tidb_cluster='%s'}[1m])) by (instance)" % self.tidb_cluster,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"],operations=operations)
        return data
    def get_all_tikv_mem_usage(self):
        """
        获取所有 TiKV mem usage
        :return: dict
        """
        operations = ["max", "average","percentile_99"]
        data=self.prome_client.get_metric_aggregation_promotion(query="avg(process_resident_memory_bytes{job=~'.*tikv',tidb_cluster='%s'}) by (instance)" % self.tidb_cluster,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"],operations=operations)
        return data
    
    def get_all_tikv_store_usage(self):
        """
        获取所有 TiKV 实例的 store usage
        :return: dict
        """
        operations = ["average"]
        used = self.prome_client.get_metric_aggregation_promotion(query="sum(tikv_store_size_bytes{type='used',tidb_cluster='%s'}) by (instance)" % self.tidb_cluster,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"],operations=operations)["average"]
        available = self.prome_client.get_metric_aggregation_promotion(query="sum(tikv_store_size_bytes{type='available',tidb_cluster='%s'}) by (instance)" % self.tidb_cluster,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"],operations=operations)["average"]
        capacity = self.prome_client.get_metric_aggregation_promotion(query="sum(tikv_store_size_bytes{type='capacity',tidb_cluster='%s'}) by (instance)" % self.tidb_cluster,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"],operations=operations)["average"]

        return {"used":used,"available":available,"capacity":capacity}

    def get_all_tiflash_instance(self):
        """
        获取所有 tiflash instances
        :return: list
        """
        data=self.prome_client.custom_query_range_promotion(query="tiflash_system_asynchronous_metric_Uptime{tidb_cluster='%s'}"  % self.tidb_cluster,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"])
        if data:
            instances = [entry['metric']['instance'].split(":")[0] for entry in data]
        else:
            instances=[]
        return instances 
    
    def get_all_tiflash_cpu_usage(self):
        """
        获取所有 tiflash cpu usage
        :return: dict
        """
        operations = ["max", "average","percentile_99"]
        data=self.prome_client.get_metric_aggregation_promotion(query="rate(tiflash_proxy_process_cpu_seconds_total{job='tiflash',tidb_cluster='%s'}[2m])"  % self.tidb_cluster,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"],operations=operations)
        return data
    def get_all_tiflash_mem_usage(self):
        """
        获取所有 tiflash mem usage
        :return: dict
        """
        operations = ["max", "average","percentile_99"]
        data=self.prome_client.get_metric_aggregation_promotion(query="tiflash_proxy_process_resident_memory_bytes{job='tiflash',tidb_cluster='%s'}" % self.tidb_cluster,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"],operations=operations)
        return data
    
    def get_all_tiflash_store_usage(self):
        """
        获取所有 tiflash store usage
        :return: dict
        """
        operations = ["average"]
        used = self.prome_client.get_metric_aggregation_promotion(query="sum(tiflash_system_current_metric_StoreSizeUsed{tidb_cluster='%s'}) by (instance)"  % self.tidb_cluster,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"],operations=operations)["average"]
        available = self.prome_client.get_metric_aggregation_promotion(query="sum(tiflash_system_current_metric_StoreSizeAvailable{tidb_cluster='%s'}) by (instance)"  % self.tidb_cluster,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"],operations=operations)["average"]
        capacity = self.prome_client.get_metric_aggregation_promotion(query="sum(tiflash_system_current_metric_StoreSizeCapacity{tidb_cluster='%s'}) by (instance)"  % self.tidb_cluster,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"],operations=operations)["average"]

        return {"used":used,"available":available,"capacity":capacity}


    def get_all_ticdc_instance(self):
        """
        获取所有 ticdc instances
        :return: list
        """
        data=self.prome_client.custom_query_range_promotion(query="process_start_time_seconds{job='ticdc',tidb_cluster='%s'}"  % self.tidb_cluster,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"])
        if data:
            instances = [entry['metric']['instance'].split(":")[0] for entry in data]
        else:
            instances=[]
        return instances 
    
    def get_all_ticdc_cpu_usage(self):
        """
        获取所有 ticdc cpu usage
        :return: dict
        """
        operations = ["max", "average","percentile_99"]
        data=self.prome_client.get_metric_aggregation_promotion(query="rate(process_cpu_seconds_total{job='ticdc',tidb_cluster='%s'}[1m])" % self.tidb_cluster,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"],operations=operations)
        return data
    def get_all_ticdc_mem_usage(self):
        """
        获取所有 ticdc mem usage
        :return: dict
        """
        operations = ["max", "average","percentile_99"]
        data=self.prome_client.get_metric_aggregation_promotion(query="process_resident_memory_bytes{job='ticdc',tidb_cluster='%s'}" % self.tidb_cluster,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"],operations=operations)
        return data

    def get_prome_client(self):
        """
        获取 Prometheus API 客户端对象
        :return: PrometheusClient 实例
        """
        if self.conf["headers"]["Authorization"]:
            prome_client = PromotionPrometheusConnect(url=self.conf["metrics_api_url"], disable_ssl=False,
                                   headers=self.conf["headers"])
        else:
            prome_client = PromotionPrometheusConnect(url=self.conf["metrics_api_url"], disable_ssl=False,
                                       headers=None)
        return prome_client
    
    
    # def get_prome_url_from_clinic_api(self):
    #     """
    #     通过 Clinic API 获取 prome_url 和 token
    #     :return: Prometheus url 地址
    #     """
    #     return self.prome_url

    # def get_custom_metric(self, query, start=None, end=None, step=60):
    #     """
    #     获取自定义的监控数据
    #     :param query: Prometheus 查询语句
    #     :param start: 查询的开始时间（Unix 时间戳）
    #     :param end: 查询的结束时间（Unix 时间戳）
    #     :param step: 查询的时间步长
    #     :return: 查询结果的 DataFrame
    #     """
    #     return self.prome_client.custom_query_range_promotion(query, start, end, step)

    def get_soft_metrics(self):
        """
        定义查询语句，获取 TiDB 监控指标数据
        :return: 查询语句字典
        """
        queries = {
            "tikv":{ "soft_metrics":{
            "Hibernate Peers(awaken)": "sum(tikv_raftstore_hibernated_peer_state{state='awaken',tidb_cluster='%s'}) by (instance)"  % self.tidb_cluster,
            "Approximate region size":"histogram_quantile(0.99, sum(rate(tikv_raftstore_region_size_bucket{tidb_cluster='%s'}[1m])) by (le))"  % self.tidb_cluster,
            "gRPC poll CPU(server.grpc-concurrency)":"sum(rate(tikv_thread_cpu_seconds_total{name=~'grpc.*',tidb_cluster='%s'}[1m])) by (instance)"  % self.tidb_cluster,
            "Scheduler worker CPU(storage.scheduler-worker-pool-size)":"sum(rate(tikv_thread_cpu_seconds_total{name=~'sched_.*',tidb_cluster='%s'}[1m])) by (instance)"  % self.tidb_cluster,
            "Store writer CPU(raftstore.store-io-pool-size)":"sum(rate(tikv_thread_cpu_seconds_total{name=~'store_write.*',tidb_cluster='%s'}[1m])) by (instance)"  % self.tidb_cluster,
            "Unified read pool CPU(readpool.unified.max-thread-count)":"sum(rate(tikv_thread_cpu_seconds_total{name=~'unified_read_po.*',tidb_cluster='%s'}[1m])) by (instance)"  % self.tidb_cluster,
            "Raft store CPU(raftstore.store-pool-size)":"sum(rate(tikv_thread_cpu_seconds_total{name=~'(raftstore|rs)_.*',tidb_cluster='%s'}[1m])) by (instance)"  % self.tidb_cluster,
            "99% Append log duration per server":"histogram_quantile(0.99, sum(rate(tikv_raftstore_append_log_duration_seconds_bucket{tidb_cluster='%s'}[1m])) by (le, instance))"  % self.tidb_cluster,
            "99% Commit log duration per server":"histogram_quantile(0.99, sum(rate(tikv_raftstore_commit_log_duration_seconds_bucket{tidb_cluster='%s'}[1m])) by (le, instance))"  % self.tidb_cluster,
            "99% Apply log duration per server":"histogram_quantile(0.99, sum(rate(tikv_raftstore_apply_log_duration_seconds_bucket{tidb_cluster='%s'}[1m])) by (le, instance))"  % self.tidb_cluster,
            "Scheduler pending commands":"sum(tikv_scheduler_contex_total{tidb_cluster='%s'}) by (instance)" % self.tidb_cluster,
            "GC tasks duration":"histogram_quantile(1, sum(rate(tikv_gcworker_gc_task_duration_vec_bucket{tidb_cluster='%s'}[1m])) by (le, task))" % self.tidb_cluster,
            "99% Handle snapshot duration":"histogram_quantile(0.99, sum(rate(tikv_raftstore_snapshot_duration_seconds_bucket{tidb_cluster='%s'}[1m])) by (le,type))" % self.tidb_cluster,
            "Compaction pending bytes":"sum(tikv_engine_pending_compaction_bytes{cf='write',tidb_cluster='%s'}) by (instance)" % self.tidb_cluster,
            "Number of Regions(avg,max)":"sum(tikv_raftstore_region_count{type='region',tidb_cluster='%s'}) by (instance)" % self.tidb_cluster,
        }}}

        queries["tidb"] = { "soft_metrics":{
            "gc life time":"max(tidb_tikvclient_gc_config{type='tikv_gc_life_time',tidb_cluster='%s'})" % self.tidb_cluster,
            "QPS(avg,max)":"sum(rate(tidb_executor_statement_total{tidb_cluster='%s'}[1m]))" % self.tidb_cluster,
            "active connections":"sum(tidb_server_tokens{tidb_cluster='%s'})" % self.tidb_cluster,
            "Stats Healthy Distribution[0,50)":"avg(tidb_statistics_stats_healthy{type='[0,50)',tidb_cluster='%s'})" % self.tidb_cluster,
            "999 Duration(insert)(avg,max)":"histogram_quantile(0.999, sum(rate(tidb_server_handle_query_duration_seconds_bucket{sql_type='Insert',tidb_cluster='%s'}[1m])) by (le,sql_type))" % self.tidb_cluster,
            "999 Duration(select)(avg,max)":"histogram_quantile(0.999, sum(rate(tidb_server_handle_query_duration_seconds_bucket{sql_type='Select',tidb_cluster='%s'}[1m])) by (le,sql_type))" % self.tidb_cluster,
            "999 Duration(update)(avg,max)":"histogram_quantile(0.999, sum(rate(tidb_server_handle_query_duration_seconds_bucket{sql_type='Update',tidb_cluster='%s'}[1m])) by (le,sql_type))" % self.tidb_cluster,
        }}

        queries["pd"] = { "soft_metrics":{
            "max-replicas":"pd_config_status{type='max-replicas',tidb_cluster='%s'}" % self.tidb_cluster,
            "Label distribution":"pd_cluster_placement_status{tidb_cluster='%s'}" % self.tidb_cluster,
            "empty-region-count":"max(pd_regions_status{type='empty-region-count',tidb_cluster='%s'})" % self.tidb_cluster,
            "Scheduler is running":"pd_scheduler_status{type='allow',tidb_cluster='%s'}" % self.tidb_cluster,
        }}

        operations = ["max", "average"]
        tikv_metrics_result=[]
        # component
        for metric_name, tikv_metric_query in queries["tikv"]["soft_metrics"].items():
            value = self.prome_client.get_metric_aggregation_promotion(query=tikv_metric_query,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"],operations=operations)
            tikv_metrics_result.append({"component":"tikv","metric_name":metric_name,"value":value})
        
        tidb_metrics_result=[]
        for metric_name, tidb_metric_query in queries["tidb"]["soft_metrics"].items():
            value = self.prome_client.get_metric_aggregation_promotion(query=tidb_metric_query,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"],operations=operations)
            tidb_metrics_result.append({"component":"tidb","metric_name":metric_name,"value":value})

        pd_metrics_result=[]
        for metric_name, pd_metric_query in queries["pd"]["soft_metrics"].items():
            if metric_name in {"empty-region-count"} :
                value = self.prome_client.get_metric_aggregation_promotion(query=pd_metric_query,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"],operations=operations)
                pd_metrics_result.append({"component":"pd","metric_name":metric_name,"value":value})
            elif metric_name in {"max-replicas"} :
                data = self.prome_client.custom_query_range_promotion(query=pd_metric_query,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"])
                value = data[0]["values"][0][1]
                pd_metrics_result.append({"component":"pd","metric_name":metric_name,"value":value})
            elif metric_name in {"Label distribution"} :
                data = self.prome_client.custom_query_range_promotion(query=pd_metric_query,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"])
                all_labels = {}
                for entry in data:
                    name = entry['metric']['name']
                    value = entry['values'][0][1]
                    all_labels[name]=value
                
                pd_metrics_result.append({"component":"pd","metric_name":metric_name,"value":all_labels})
            elif metric_name in {"Scheduler is running"} :
                data = self.prome_client.custom_query_range_promotion(query=pd_metric_query,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"])
                all_labels = {}
                for entry in data:
                    name = entry['metric']['kind']
                    value = entry['values'][0][1]
                    all_labels[name]=value
                pd_metrics_result.append({"component":"pd","metric_name":metric_name,"value":all_labels})
            else:
                value = self.prome_client.custom_query_range_promotion(query=pd_metric_query,start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"])
                pd_metrics_result.append({"component":"pd","metric_name":metric_name,"value":value})

        return tikv_metrics_result+tidb_metrics_result+pd_metrics_result
    
    def get_physical_metrics(self):

        all_instances_cpu_capacity=self.get_all_instances_cpu_capacity()
        all_instances_mem_capacity=self.get_all_instances_mem_capacity()
        tidb_instances=self.get_all_tidb_instance()
        tidb_instances_cpu_usage=self.get_all_tidb_cpu_usage() 
        tidb_instances_mem_usage=self.get_all_tidb_mem_usage()
        tidb_physical_metrics=[
            {
                "component":"tidb",
                'instance':instance,
                'cpu capacity':all_instances_cpu_capacity[instance],
                'mem capacity':all_instances_mem_capacity[instance],
                'cpu usage':tidb_instances_cpu_usage,
                "mem usage":tidb_instances_mem_usage,
                "store_usage":0,
                "instance number":len(tidb_instances),
            }
            for instance in tidb_instances
        ]

        pd_instances=self.get_all_pd_instance()
        pd_instances_cpu_usage=self.get_all_pd_cpu_usage()
        pd_instances_mem_usage=self.get_all_pd_mem_usage()

        pd_physical_metrics=[
            {
                "component":"pd",
                'instance':instance,
                'cpu capacity':all_instances_cpu_capacity[instance],
                'mem capacity':all_instances_mem_capacity[instance],
                'cpu usage':pd_instances_cpu_usage,
                "mem usage":pd_instances_mem_usage,
                "store_usage":0,
                "instance number":len(pd_instances),
            }
            for instance in pd_instances
        ]
        tikv_instances=self.get_all_tikv_instance()
        tikv_instances_cpu_usage=self.get_all_tikv_cpu_usage()
        tikv_instances_mem_usage=self.get_all_tikv_mem_usage()
        tikv_instances_store_usage=self.get_all_tikv_store_usage()

        tikv_physical_metrics=[
            {
                "component":"tikv",
                'instance':instance,
                'cpu capacity':all_instances_cpu_capacity[instance],
                'mem capacity':all_instances_mem_capacity[instance],
                'cpu usage':tikv_instances_cpu_usage,
                "mem usage":tikv_instances_mem_usage,
                "store_usage":tikv_instances_store_usage,
                "instance number":len(tikv_instances),
            }
            for instance in tikv_instances
        ]
        tiflash_instances=self.get_all_tiflash_instance()
        # tiflash_instances_cpu_usage=self.get_all_tiflash_cpu_usage()
        if tiflash_instances:
            tiflash_instances_cpu_usage=self.get_all_tiflash_cpu_usage()
            tiflash_instances_mem_usage=self.get_all_tiflash_mem_usage()
            tiflash_instances_store_usage=self.get_all_tiflash_store_usage()
            tiflash_physical_metrics=[
                {
                    "component":"tiflash",
                    'instance':instance,
                    'cpu capacity':all_instances_cpu_capacity[instance],
                    'mem capacity':all_instances_mem_capacity[instance],
                    'cpu usage':tiflash_instances_cpu_usage,
                    "mem usage":tiflash_instances_mem_usage,
                    "store_usage":tiflash_instances_store_usage,
                    "instance number":len(tiflash_instances),
                }
                for instance in tiflash_instances
            ]   
            
        else:
            tiflash_physical_metrics=[]

        ticdc_instances=self.get_all_ticdc_instance()
        if ticdc_instances:
            ticdc_instances_cpu_usage=self.get_all_ticdc_cpu_usage()
            ticdc_instances_mem_usage=self.get_all_ticdc_mem_usage()
            ticdc_physical_metrics=[
                {
                    "component":"ticdc",
                    'instance':instance,
                    'cpu capacity':all_instances_cpu_capacity[instance],
                    'mem capacity':all_instances_mem_capacity[instance],
                    'cpu usage':ticdc_instances_cpu_usage,
                    "mem usage":ticdc_instances_mem_usage,
                    "store_usage":0,
                    "instance number":len(ticdc_instances),
                }
                for instance in ticdc_instances
            ]   
            
        else:
            ticdc_physical_metrics=[]
        return tidb_physical_metrics+tikv_physical_metrics+tiflash_physical_metrics+pd_physical_metrics+ticdc_physical_metrics

    def get_raw_data(self, query, start_time, end_time, step):
        """
        获取原始数据
        :param query: Prometheus 查询语句
        :param start_time: 查询的开始时间（Unix 时间戳）
        :param end_time: 查询的结束时间（Unix 时间戳）
        :param step: 查询的时间间隔
        :return: 原始数据的 DataFrame
        """
        return self.get_custom_metric(query, start_time, end_time, step)

    def capacity_assessment(self, data):
        """
        容量评估，检查 TiDB 集群的负载情况
        :param data: 监控数据的 DataFrame
        :return: 容量评估结果（示例：是否需要扩展资源）
        """
        # 示例：假设 QPS > 1000 时需要扩展资源
        if data['value'].mean() > 1000:
            return "Capacity Warning: Need to scale up resources"
        else:
            return "Capacity is within limits"

    def inspection(self):
        """
        TiDB 集群巡检，检查系统是否出现异常
        :param data: 监控数据的 DataFrame
        :return: 巡检结果
        """
        operations = ["max", "average", "percentile_50", "percentile_75", "percentile_80", "percentile_85",
                        "percentile_90", "percentile_95", "percentile_99", "percentile_99.9"]
        data=self.prome_client.get_metric_aggregation_promotion(query=self.queries["qps"],start_time=self.conf["start_time"],end_time=self.conf["end_time"],step=self.conf["step_in_seconds"],operations=operations)
        print(data)