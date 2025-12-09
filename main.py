import sys
import datetime
from health_checker.health_checker import HealthChecker
from utils.logger import setup_logger
from utils import helpers
from tidb_cluster.configer import Configer
from capacity_planner.capacity_planner import CapacityPlanner
from tidb_cluster.tidb_cluster import TiDBCluster
from tidb_cluster.op_tidb_cluster import OpTidbCluster
import click
from lark.app import LarkApp
import utils
from tidb_cluster.init_op_conf import TidbOpConfig
# from tidb_cluster.init_ec2_conf import InitEC2

# consts
health_check_type = ["all", "tidb", "tikv", "pd", "tiflash"]
talent_bz_dynamic = ["talent"]
tidb_inspection = ["all"]
init_ec2_all = ["all"]
#k8s_prom_url = "https://www.ds.us-east-1.aws.observability.tidbcloud.com/internal/metrics/d5d1a915-1d37-22a7-82b8-8cb67cc57820" # hardcode first


@click.group()
def cli():
    click.echo('Welcome to TiDBCloud Capacity Planner and Health Checker!')

# @cli.command()
# @click.option('--init', '-n', prompt=True, type=click.Choice(init_ec2_all), default='all', help='init ec2')
# def init_ec2(init):
#     # 1. 初始化 init ec2 对象
#     # init_ec2 = InitEC2("tidbcloud.yaml")
#     # init_ec2.execute_all()
    

@cli.command()
@click.option('--inspection', '-i', prompt=True, type=click.Choice(tidb_inspection), default='all', help='tidb inspection')
def inspection(inspection):
    # if inspection == 'all':
    #     click.confirm("Have you connected to FeiLian?", abort=True)
    # 1. 初始化 OP 配置
    conf = TidbOpConfig("tidbcloud.yaml").set_conf()
    # 2. 初始化 TiDBOP 对象
    tidb_op_cluster = OpTidbCluster(conf)
    # https://clinic.pingcap.com/clinic/api/v1/data/metrics?query=tidb_server_connections&start=1734937200&end=1734944400&step=60
    physical_metrics=tidb_op_cluster.get_physical_metrics()
    helpers.save_list_to_csv(physical_metrics,filename="physical_metrics",format="row")
    soft_metrics=tidb_op_cluster.get_soft_metrics()
    # soft_metrics={'Hibernate Peers(awaken)': {'max': 7271.0, 'average': 2053.137037037037}, 'Approximate region size': {'max': 263995946.53538463, 'average': 257928625.25189564}, 'gRPC poll CPU(server.grpc-concurrency)': {'max': 0.7518333333307623, 'average': 0.5345541152263403}, 'Scheduler worker CPU(storage.scheduler-worker-pool-size)': {'max': 0.35833333333430345, 'average': 0.31194259259258833}, 'Store writer CPU(raftstore.store-io-pool-size)': {'max': 0.25466666666713234, 'average': 0.21081337448559967}, 'Unified read pool CPU(readpool.unified.max-thread-count)': {'max': 0.2946666666665503, 'average': 0.1770224279835463}, 'Raft store CPU(raftstore.store-pool-size)': {'max': 0.9101666666664339, 'average': 0.6311932098765238}, '99% Append log duration per server': {'max': 0.002171064201381145, 'average': 0.0013942784207883797}, '99% Commit log duration per server': {'max': 0.0046268036669784894, 'average': 0.003145537350951968}, '99% Apply log duration per server': {'max': 0.0011762149851399964, 'average': 0.0011399796779664828}, 'Scheduler pending commands': {'max': 15.0, 'average': 3.4962962962962965}, 'GC tasks duration': {'max': 0.32768, 'average': 0.0183775}, '99% Handle snapshot duration': {'max': 1.3041664000000002, 'average': 0.6096896}, 'Compaction pending bytes': {'max': 3691677897.0, 'average': 233959924.5}, 'Number of Regions(avg,max)': {'max': 37258.0, 'average': 36898.25555555556}, 'gc life time': {'max': 86400.0, 'average': 86400.0}, 'QPS(avg,max)': {'max': 14148.616666666667, 'average': 13872.506481481483}, 'active connections': {'max': 38.0, 'average': 26.7}, 'Stats Healthy Distribution[0,50)': {'max': 18.22222222222222, 'average': 13.9}, '999 Duration(insert)(avg,max)': {'max': 0.01115784501844997, 'average': 0.009561514230321038}, '999 Duration(select)(avg,max)': {'max': 0.007997720556824036, 'average': 0.007984084814030071}, '999 Duration(update)(avg,max)': {'max': 0.003998, 'average': 0.0014432222222222223}, 'max-replicas': '3', 'Label distribution': {'az:A': '3', 'az:B': '3', 'az:C': '3', 'host:h106': '1', 'host:h144': '1', 'host:h2.95': '1', 'host:h4.95': '1', 'host:h89': '1', 'host:h90': '1', 'host:h91': '1', 'host:h94': '1', 'host:h96': '1', 'zone:SG': '9'}, 'empty-region-count': {'max': 53.0, 'average': 53.0}, 'Scheduler is running': {'balance-hot-region-scheduler': '1', 'balance-leader-scheduler': '1', 'balance-region-scheduler': '1', 'balance-witness-scheduler': '1', 'evict-slow-store-scheduler': '1', 'split-bucket-scheduler': '1', 'transfer-witness-leader-scheduler': '1'}}
    helpers.save_list_to_csv(soft_metrics,filename="soft_metrics",format="row")


@cli.command()
@click.option('--business', '-b', prompt=True, type=click.Choice(talent_bz_dynamic), default='talent', help='business dynamic')
def cluster_info(business):
    if business == 'talent':
        click.confirm("Have you connected to FeiLian?", abort=True)
        # 1. 获取租户下所有的 clusters
    conf = Configer("tidbcloud.yaml").set_conf()
    tidb_cluster = TiDBCluster(conf)
    clusters = tidb_cluster.get_dedicated_clusters_by_tenant_from_k8s()
    clusters_instance_type = tidb_cluster.get_clusters_basic_info_by_tenant_from_k8s()
    # 2. 遍历 clusters，收集硬件指标(组件，对应机型，节点数)和 QPS

    # conf['capacity']['cluster_list']
    
    # end_time = datetime.datetime.now()
    # start_time = end_time - datetime.timedelta(days=1)

    end_time = helpers.convert_datetime(conf['prometheus']['end_time'])
    start_time = helpers.convert_datetime(conf['prometheus']['start_time'])
    operations=['max']
    clusters_qps_and_nodecount = tidb_cluster.get_basic_info_by_clusters(clusters,start_time,end_time,operations)

    # 3. 获取 clusters 集群名称，集群版本
    clusters_name_and_version = tidb_cluster.get_cluster_basic_info_by_ai()
    # print(clusters_name_and_version)
    # print(type(clusters_name_and_version))

    # 4. 将收集的数据汇总
    # clusters_name_and_version,clusters_instance_type,clusters_qps_and_nodecount
    # 合并 clusters_name_and_version 和 clusters_qps_and_nodecount 信息
    merge_qps_and_nodecount={
                    'PD 节点数':'pd',
                    'TiDB 节点数':'tidb',
                    'TiKV 节点数':'tikv',
                    'TiFlash 节点数':'tiflash',
                    'Total QPS(MAX)':'qps',
                    '实际数据存储量(byte)':'data_size'
                }
        
    merged_res=utils.helpers.merged_list_through_dict_key_value(clusters_name_and_version,clusters_qps_and_nodecount,"cluster_id",merge_qps_and_nodecount)
    # logger.info("first merged_res: {} ".format(merged_res))
    
    # 合并 merged_res 和 clusters_instance_type 信息

    merge_instance_type={
        '组件':'component',
        '实例类型':'component_instance_type',
        'CPU(core)': 'CPU(core)',
        'Memory(byte)': 'Memory(byte)',
    }
    merged_res=utils.helpers.merged_list_through_dict_key_value_and_combine_custom_kv(merged_res,clusters_instance_type,"cluster_id",merge_instance_type,True)
    # logger.info("second merged_res: {} ".format(merged_res))
    merged_res=utils.helpers.deduplicate_use_custom_key(merged_res,"cluster_id")
    # logger.info("third merged_res: {} ".format(merged_res))

    headers=['cluster_id', 'cluster_name', 'version', 'PD 节点数', 'TiDB 节点数', 'TiKV 节点数', 'TiFlash 节点数', 'Total QPS(MAX)', '实际数据存储量(byte)', '组件tikv', '组件tidb', '组件pd', '组件tiflash']

    
    merged_res=utils.helpers.keep_same_headers(merged_res,headers)
    # 打印合并后的结果


    utils.helpers.write_dictlist_to_csv(merged_res,tidb_cluster.csv_file_name)
    

@cli.command()
@click.option('--mode', '-m', prompt=True, type=click.Choice(['all', 'node', 'cluster']), default='all', help='capacity planner mode')
def capacity(mode):
    if mode == 'all' or mode == 'node':
        click.confirm("Have you connected to FeiLian?", abort=True)
    # 1. 遍历 cluster list
    # 2. 遍历 water list
    # 3. 每种组合赋值 conf 集群信息
    # 4. 调用 generate_capacity_plan
    # tidb_cluster = TiDBCluster(conf)
    conf = Configer("tidbcloud.yaml").set_conf()
    cluster_list=conf['capacity']['cluster_list']
    watermark_list=conf['capacity']['plan_resource_redundancy_x_list']
    for c in cluster_list:
        for w in watermark_list:
            conf['cluster_info']['cluster_id'] = c
            conf['capacity']['plan_resource_redundancy_x']=w
            capacity_planner = CapacityPlanner(conf)
            capacity_planner.generate_capacity_plan(mode)


@cli.command()
@click.option('--type', '-t', prompt=True, type=click.Choice(health_check_type), default='all', help='health check type')
@click.option('--report', '-r', prompt=True, type=click.Choice(['console']), default='console', help='report channel')
def health_check(type, report):
    conf = Configer("tidbcloud.yaml").set_conf()
    tidb_cluster = TiDBCluster(conf)
    if type == 'tiflash':
        if not tidb_cluster.validate_component(type):
            logger.info("Cluster {} doesn't have any {} instances.".format(conf['cluster_info']['cluster_id'], type))
            sys.exit(0)
    health_checker = HealthChecker(conf, health_check_type)
    health_checker.check_health(type, report)


@cli.command()
@click.option('--write', '-w', prompt=True, type=click.Choice(['Yes', 'No']), default='Yes', help='Write to spreadsheet')
def list_clusters(write):
    conf = Configer("tidbcloud.yaml").set_conf()
    tidb_cluster = TiDBCluster(conf)
    clusters = tidb_cluster.get_dedicated_clusters_by_tenant_from_k8s()
    components_list = [['TenantID', 'ProjectID', 'ClusterID', 'TiDB_Cnt', 'TiDB_CPU', 'TiDB_Memory(byte)', 'PD_Cnt', 'PD_CPU', 'PD_Memory(byte)', 'TiKV_Cnt', 'TiKV_CPU', 'TiKV_Memory(byte)', 'TiFlash_Cnt', 'TiFlash_CPU', 'TiFlash_Memory(byte)']]
    for cluster in clusters:
        conf['cluster_info'] = cluster
        new_cluster = TiDBCluster(conf)
        components = new_cluster.get_components_from_k8s()

        capacity = {}
        for component in components.keys():
            instances = new_cluster.get_instances_by_component(component)
            ec2_type = list(instances[0].values())[0]
            capacity[component] = new_cluster.get_capacity_by_instance_type(ec2_type)

        if 'tiflash' in components:
            components_node_count_list = [cluster['tenant_id'], cluster['project_id'], cluster['cluster_id'], int(components['tidb']), int(capacity['tidb']['CPU(core)']), int(capacity['tidb']['Memory(byte)']), int(components['pd']), int(capacity['pd']['CPU(core)']), int(capacity['pd']['Memory(byte)']), int(components['tikv']), int(capacity['tikv']['CPU(core)']), int(capacity['tikv']['Memory(byte)']), int(components['tiflash']), int(capacity['tiflash']['CPU(core)']), int(capacity['tiflash']['Memory(byte)'])]
            print("Cluster ID: {} Project ID: {} Tenant ID: {} TiDB Count: {} TiDB CPU: {} TiDB Memory: {} PD Count: {} PD CPU: {} PD Memory: {} TiKV Count: {} TiKV CPU: {} TiKV Memory:{} TiFlash Count: {} TiFlash CPU: {} TiFlash Memory: {}".format(cluster['cluster_id'], cluster['project_id'], cluster['tenant_id'], components['tidb'], capacity['tidb']['CPU(core)'], capacity['tidb']['Memory(byte)'], components['pd'], capacity['pd']['CPU(core)'], capacity['pd']['Memory(byte)'], components['tikv'], capacity['tikv']['CPU(core)'], capacity['tikv']['Memory(byte)'], components['tiflash'], capacity['tiflash']['CPU(core)'], capacity['tiflash']['Memory(byte)']))
        else:
            components_node_count_list = [cluster['tenant_id'], cluster['project_id'], cluster['cluster_id'], int(components['tidb']), int(capacity['tidb']['CPU(core)']), int(capacity['tidb']['Memory(byte)']), int(components['pd']), int(capacity['pd']['CPU(core)']), int(capacity['pd']['Memory(byte)']), int(components['tikv']), int(capacity['tikv']['CPU(core)']), int(capacity['tikv']['Memory(byte)']), 0, 0, 0]
            print("Cluster ID: {} Project ID: {} Tenant ID: {} TiDB Count: {} TiDB CPU: {} TiDB Memory: {} PD Count: {} PD CPU: {} PD Memory: {} TiKV Count: {} TiKV CPU: {} TiKV Memory:{}".format(cluster['cluster_id'],
                                                                                             cluster['project_id'],
                                                                                             cluster['tenant_id'],
                                                                                             components['tidb'],
                                                                                             capacity['tidb']['CPU(core)'],
                                                                                             capacity['tidb']['Memory(byte)'],
                                                                                             components['pd'],
                                                                                              capacity['pd']['CPU(core)'],
                                                                                             capacity['pd']['Memory(byte)'],
                                                                                             components['tikv'],
                                                                                            capacity['tikv']['CPU(core)'],
                                                                                            capacity['tikv']['Memory(byte)']
                                                                                             ))
        components_list.append(components_node_count_list)

    if write == 'Yes':
        components_list.append(["更新时间: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))])
        lark = LarkApp(conf)
        lark.write_sheet(components_list)


if __name__ == '__main__':
    # conf = Configer("tidbcloud.yaml").set_conf()
    # logger = setup_logger(__name__, conf['logging']['file_name'], conf['logging']['level'])
    cli()