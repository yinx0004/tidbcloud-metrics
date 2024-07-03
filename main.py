import sys
import datetime
from health_checker.health_checker import HealthChecker
from utils.logger import setup_logger
from tidb_cluster.configer import Configer
from capacity_planner.capacity_planner import CapacityPlanner
from tidb_cluster.tidb_cluster import TiDBCluster
import click
from lark.app import LarkApp

# consts
health_check_type = ["all", "tidb", "tikv", "pd", "tiflash"]
#k8s_prom_url = "https://www.ds.us-east-1.aws.observability.tidbcloud.com/internal/metrics/d5d1a915-1d37-22a7-82b8-8cb67cc57820" # hardcode first


@click.group()
def cli():
    click.echo('Welcome to TiDBCloud Capacity Planner and Health Checker!')


@cli.command()
@click.option('--mode', '-m', prompt=True, type=click.Choice(['all', 'node', 'cluster']), default='all', help='capacity planner mode')
def capacity(mode):
    if mode == 'all' or mode == 'node':
        click.confirm("Have you connected to FeiLian?", abort=True)
    capacity_planner = CapacityPlanner(conf)
    capacity_planner.generate_capacity_plan(mode)


@cli.command()
@click.option('--type', '-t', prompt=True, type=click.Choice(health_check_type), default='all', help='health check type')
@click.option('--report', '-r', prompt=True, type=click.Choice(['console']), default='console', help='report channel')
def health_check(type, report):
    if type == 'tiflash':
        if not tidb_cluster.validate_component(type):
            logger.info("Cluster {} doesn't have any {} instances.".format(conf['cluster_info']['cluster_id'], type))
            sys.exit(0)
    health_checker = HealthChecker(conf, health_check_type)
    health_checker.check_health(type, report)


@cli.command()
@click.option('--write', '-w', prompt=True, type=click.Choice(['Yes', 'No']), default='Yes', help='Write to spreadsheet')
def list_clusters(write):
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
    conf = Configer("tidbcloud.yaml").set_conf()
    logger = setup_logger(__name__, conf['logging']['file_name'], conf['logging']['level'])
    tidb_cluster = TiDBCluster(conf)
    cli()


