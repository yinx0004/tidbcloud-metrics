import sys
import datetime
from health_checker.health_checker import HealthChecker
from utils.logger import setup_logger
from tidb_cluster.configer import Configer
from capacity_planner.capacity_planner import CapacityPlanner
from tidb_cluster.tidb_cluster import TiDBCluster
import click
from lark.app import LarkApp
from prometheus_api_client import PrometheusConnect
from prometheus.cloud_prom_query import health_query
import json
import requests
import utils
import ai.ai

# def deduplicate_dict_list(original_list, key):
#     seen = set()
#     unique_list = []
    
#     for d in original_list:
#         value = d.get(key)
#         if value not in seen:
#             seen.add(value)
#             unique_list.append(d)
    
#     return unique_list
# def append_unique_data(data_set, new_data):
#     if new_data not in data_set:
#         data_set.add(new_data)



if __name__ == '__main__':
    # conf = Configer("tidbcloud.yaml").set_conf()
    # logger = setup_logger(__name__, conf['logging']['file_name'], conf['logging']['level'])
    # tidb_cluster = TiDBCluster(conf)
    # url='https://www.ds.us-east-1.aws.observability.tidbcloud.com/internal/metrics/d5d1a915-1d37-22a7-82b8-8cb67cc57820'
    # print(conf['prometheus']['cluster_prom_id_token'])

    # k8s 
    # url='https://www.ds.us-east-1.aws.observability.tidbcloud.com/internal/metrics/d5d1a915-1d37-22a7-82b8-8cb67cc57820'
    # client = PrometheusConnect(url=url, disable_ssl=False,
                                    #    headers=None)
    # print(client.custom_query(query='(time() - process_start_time_seconds{component="tidb"})'))                                   
    # cloud
    # url='https://www.ds.us-east-1.aws.observability.tidbcloud.com/external/metrics/tidbcloud/tenant/1372813089209061633/project/1372813089454521730/application/1379661944646413610'
    # token='eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlJEWTNNVUpGTUVReU9VVTBSa0U1TXpCRk5rRkRRVEl3UkRNMU0wSXpNelJHUVRrMVFUbEZRZyJ9.eyJodHRwczovL3RpZGJjbG91ZC5jb20vbGFzdF9wYXNzd29yZF9yZXNldCI6IjIwMjQtMDctMThUMTI6MjY6NTYuMjA1WiIsImh0dHBzOi8vdGlkYmNsb3VkLmNvbS9sb2dpbl9yZWNlaXZlZF9hdCI6MTcyNTUzOTIzMzc1MCwibG9naW5faGFzX29yZyI6IjEiLCJsb2dpbl9vcmdfdHlwZSI6InBlcnNvbmFsIiwibG9naW5fb3JnX2lkIjoiMSIsImxvZ2luX2NvbXBhbnlfbmFtZSI6IiIsImVtYWlsIjoieXVlY2hhbmdxaWFuZ0BwaW5nY2FwLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJpc3MiOiJodHRwczovL3RpZGIuYXV0aDAuY29tLyIsImF1ZCI6IjZJWnRoQ2ZtUktJUEVuUVNUOGFEYnRNN1NHZE1uaVJsIiwiaWF0IjoxNzI1NTM5MjMzLCJleHAiOjE3MjU1NzUyMzMsInN1YiI6ImF1dGgwfDYxY2E3MzY4ZTk1Njc1MDA2ODJhZDE4MiIsImF0X2hhc2giOiIwQ1FxNkdNMFB0ZmtLaC03ZG9TTW5RIiwic2lkIjoiQ1ZoX2RrbGw1c0RBV0dkbFlXUXZTUXZ3T25XUE5uSnYiLCJub25jZSI6IndEeWFUcmdzY1BTd3l0VU5LTVhDZUpHeUZOZXJ1TlBMIn0.O9IXssN9Si9VzKytOG-8-rnsKjxz4ClJ3FG6ct2fFPSTU1HqThAYC3fwF1OPIHPyqtYQYUEqFb7rtCj60zZRydT8mwRJ7jRv5LLbyq-oeA9emt1_HP-DPq4FY2DPO1KrFK4XuL8eadkhhtPozhkSt9-lE6KX_CrcEqrqByVfDTZHenrqziUtxmhCriQ_bgVB7Q2EyG3XnhUJIx3ebnidpOobpP6Y5m-CUzQ8AetVx1y1feET8uywsw7tEdRoytO7SJFmtlYxlNRor7dxkb1M3SKKZnYk-OoEISX2jG7L_u8WW6x8ZAaQTjEifrz5yllurzMeBjydXsEJ08onZRiPsQ'
    # client = PrometheusConnect(url=url, disable_ssl=False,
    #                                headers={"Authorization": "bearer {}".format(token)})
    # print(client.custom_query(query='kube_node_labels{tenant="1372813089209061633",label_cluster="1379661944646413610",label_component="tidb"}'))
    # current_time = datetime.datetime.now()
    # one_day_ago = current_time - datetime.timedelta(days=1)
    # # print(client.custom_query(query="all"))
    # print(client.get_metric_aggregation(query="dbaas_tidb_cluster_info",
    #         start_time=one_day_ago, end_time=current_time, step=60,
    #         operations=["max"])
    # )

    # token='eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlJEWTNNVUpGTUVReU9VVTBSa0U1TXpCRk5rRkRRVEl3UkRNMU0wSXpNelJHUVRrMVFUbEZRZyJ9.eyJodHRwczovL3RpZGJjbG91ZC5jb20vbGFzdF9wYXNzd29yZF9yZXNldCI6IjIwMjQtMDctMThUMTI6MjY6NTYuMjA1WiIsImh0dHBzOi8vdGlkYmNsb3VkLmNvbS9sb2dpbl9yZWNlaXZlZF9hdCI6MTcyMTgwMTkwMjQ2OCwibG9naW5faGFzX29yZyI6IjEiLCJsb2dpbl9vcmdfdHlwZSI6InBlcnNvbmFsIiwibG9naW5fb3JnX2lkIjoiMSIsImxvZ2luX2NvbXBhbnlfbmFtZSI6IiIsImVtYWlsIjoieXVlY2hhbmdxaWFuZ0BwaW5nY2FwLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJpc3MiOiJodHRwczovL3RpZGIuYXV0aDAuY29tLyIsImF1ZCI6IjZJWnRoQ2ZtUktJUEVuUVNUOGFEYnRNN1NHZE1uaVJsIiwiaWF0IjoxNzIxODAxOTAyLCJleHAiOjE3MjE4Mzc5MDIsInN1YiI6ImF1dGgwfDYxY2E3MzY4ZTk1Njc1MDA2ODJhZDE4MiIsImF0X2hhc2giOiJydUJMMVlEa25FbldzSDFzTDZYblJnIiwic2lkIjoicWhUYTJHczN4Y0VxN2VYdk9pZWFqZC1zTk83T0hOQkEiLCJub25jZSI6Ik5VV3dla2dKaU5Hb0JoWHNXWWZRWHd3dWdHd2JTRnV1In0.z0YZQhfWjbZiGGW_rwHNsh73XxIZkHvnB4BUWGslAPeNnsboSfTaveFzY003gVLliObs8ag2KP5a9SjuEsDqImlLHkvLNp0WvATrY3_bOGxzphwiU1Y1xjB-m9qnPV9XV-ps2FXMEF5_U88En5JfCUycfnMw97hzGgLIj7169h6z-vMTEAygGonGtG3RXcFkME9Z2hngdvvtqhdIEFCRQWe_q79OEQdfpj_rfxUktUsGgfJ1961y0n6lfLed88d7oIYv8a1Q0q6Nc6330Cq1CUPOgdikjWgPdWseK9PnZw9bWxHKniciu6VhNBr2rm65zdVewX0T9sCcGVINcNBXJg'
    #        eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlJEWTNNVUpGTUVReU9VVTBSa0U1TXpCRk5rRkRRVEl3UkRNMU0wSXpNelJHUVRrMVFUbEZRZyJ9
    # client = PrometheusConnect(url=url, disable_ssl=False,
    #                     cl           headers={"Authorization": "bearer {}".format(token)})

    # print(client.custom_query('(time() - process_start_time_seconds{component="tidb"})'))
# ----------------

    # conf = Configer("tidbcloud.yaml").set_conf()
    # logger = setup_logger(__name__, conf['logging']['file_name'], conf['logging']['level'])
    # tidb_cluster = TiDBCluster(conf)

    # get_url='https://linguflow.pingcap.net/linguflow-api/interactions/e27b9e07-4a59-409d-874c-8b91d7e6805d'
    # ai_test = ai.ai.AI()
    # data=ai_test.get_data_with_retry(input_id={'id':'e27b9e07-4a59-409d-874c-8b91d7e6805d'})
    # print(data)

    # print(tidb_cluster.csv_file_name)
    # # 1. 获取租户下所有的 clusters
    # clusters = tidb_cluster.get_dedicated_clusters_by_tenant_from_k8s()
    # clusters_instance_type = tidb_cluster.get_clusters_basic_info_by_tenant_from_k8s()
    # # 2. 遍历 clusters，收集硬件指标(组件，对应机型，节点数)和 QPS
    # end_time = datetime.datetime.now()
    # start_time = end_time - datetime.timedelta(days=1)
    # operations=['max']
    # clusters_qps_and_nodecount = tidb_cluster.get_basic_info_by_clusters(clusters,start_time,end_time,operations)

    # # 3. 获取 clusters 集群名称，集群版本
    # clusters_name_and_version = tidb_cluster.get_cluster_basic_info_by_ai()
    # # print(clusters_name_and_version)
    # # print(type(clusters_name_and_version))

    # # 4. 将收集的数据汇总
    # # clusters_name_and_version,clusters_instance_type,clusters_qps_and_nodecount
    # # 合并 clusters_name_and_version 和 clusters_qps_and_nodecount 信息
    # merge_qps_and_nodecount={
    #                 'PD 节点数':'pd',
    #                 'TiDB 节点数':'tidb',
    #                 'TiKV 节点数':'tikv',
    #                 'TiFlash 节点数':'tiflash',
    #                 'Total QPS(MAX)':'qps'
    #             }
        
    # merged_res=utils.helpers.merged_list_through_dict_key_value(clusters_name_and_version,clusters_qps_and_nodecount,"cluster_id",merge_qps_and_nodecount)
    # # 合并 merged_res 和 clusters_instance_type 信息

    # merge_instance_type={
    #     '组件':'component',
    #     '实例类型':'component_instance_type',
    #     'CPU(core)': 'CPU(core)',
    #     'Memory(byte)': 'Memory(byte)',
    # }
    # merged_res=utils.helpers.merged_list_through_dict_key_value_and_combine_custom_kv(merged_res,clusters_instance_type,"cluster_id",merge_instance_type,True)
    # # 打印合并后的结果

    # utils.helpers.write_dictlist_to_csv(merged_res,tidb_cluster.csv_file_name)
# ----------
    # 5. 按照要求将所有数据按照格式输出
    # print(clusters_basic_info)
    # print(tidb_cluster.get_cluster_basic_info_by_ai())
    # response = requests.get(url="https://linguflow.pingcap.net/linguflow-api/interactions/f5497864-7c80-4535-9a95-df860b656c5a",verify=False,headers={'x-linguflow-access-key':'654b5c8a8860c40200dfb836','x-linguflow-access-secret':'f117aab6a2180c4424be069d645022b4','x-linguflow-user':'xq'})

    # print(response.json().get('interaction').get('output'))


    # 给定的包含表格分隔符的数据
    # clusters_name_and_version=[{"cluster_id": "1379661944646414008","cluster_name": "prod-seamless-wallet-03","version": "v6.5.9"}]
    # clusters_qps_and_nodecount=[{'tenant_id': '1372813089209061633', 'project_id': '1372813089454525346', 'cluster_id': '1379661944646414008', 'pd': '3', 'tidb': '55', 'tiflash': '6', 'tikv': '69', 'qps': {'max': 129338.91666666667}}]
    # clusters_instance_type=[{'tenant_id': '1372813089209061633', 'project_id': '1372813089454536089', 'cluster_id': '1379661944646414008', 'component': 'tidb', 'component_instance_type': 'm6g.xlarge', 'CPU(core)': 4, 'Memory(byte)': 17179869184, 'NetworkIn Bandwidth(byte)': 167772160, 'NetworkOut Bandwidth(byte)': 167772160, 'Disk Bandwidth(byte)': 131072000, 'Disk IOPS': 3000}]
    

    # 原始列表，包含字典元素
    # original_list = [
    #     {'key1': 'value1', 'key2': 'value2'},
    #     {'key1': 'value3', 'key2': 'value2'},
    #     {'key1': 'value1', 'key2': 'value2'}
    # ]

    # # 指定要去重的键
    # key_to_check = 'key1'

    # # 调用函数进行按指定键去重操作
    # unique_list = deduplicate_dict_list(original_list, key_to_check)

    # print(unique_list)
    # data=[{'cluster_id': '10273184600749456107', 'cluster_name': 'prod-seamless-jili', 'version': 'v7.5.3', 'PD 节点数': '3', 'TiDB 节点数': '16', 'TiKV 节点数': '39', 'TiFlash 节点数': 0, 'Total QPS(MAX)': {'max': 168034.00833333333}, '实际数据存储量(byte)': {'max': 76868039144706.0}, '组件tidb': '实例类型:c6g.4xlarge  CPU(core):16  Memory(byte):34359738368  ', '组件pd': '实例类型:c6g.4xlarge  CPU(core):16  Memory(byte):34359738368  ', '组件tikv': '实例类型:m6g.8xlarge  CPU(core):32  Memory(byte):137438953472  '}]

    # headers=['cluster_id', 'cluster_name', 'version', 'PD 节点数', 'TiDB 节点数', 'TiKV 节点数', 'TiFlash 节点数', 'Total QPS(MAX)', '实际数据存储量(byte)', '组件tikv', '组件tidb', '组件pd', '组件tiflash']

    # result = format_json(data, headers)
    # print(result)