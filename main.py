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
    components_list = [['TenantID', 'ProjectID', 'ClusterID', 'TiDB_Cnt', 'PD_Cnt', 'TiKV_Cnt', 'TiFlash_Cnt']]
    #components_list = [['TenantID', 'ProjectID', 'ClusterID', 'TiDB_Cnt', 'TiDB_CPU', 'TiDB_Memory(GB)', 'PD_Cnt', 'PD_CPU', 'PD_Memory(GB)', 'TiKV_Cnt', 'TiKV_CPU', 'TiKV_Memory(GB)', 'TiKV_Storage(GB)', 'TiFlash_Cnt', 'TiFlash_CPU', 'TiFlash_Memory(GB)', 'TiFlash_Storage(GB)']]
    for cluster in clusters:
        conf['cluster_info'] = cluster
        new_cluster = TiDBCluster(conf)
        components = new_cluster.get_components_from_k8s()
        #components = new_cluster.get_components_from_cloud()

        if 'tiflash' in components:
            components_node_count_list = [cluster['tenant_id'], cluster['project_id'], cluster['cluster_id'], int(components['tidb']), int(components['pd']), int(components['tikv']), int(components['tiflash'])]
            print("Cluster ID: {} Project ID: {} Tenant ID: {} TiDB: {} TiKV: {} TiFlash: {}".format(cluster['cluster_id'], cluster['project_id'], cluster['tenant_id'], components['tidb'], components['tikv'], components['tiflash']))
        else:
            components_node_count_list = [cluster['tenant_id'], cluster['project_id'], cluster['cluster_id'], int(components['tidb']), int(components['pd']), int(components['tikv']), 0]
            print("Cluster ID: {} Project ID: {} Tenant ID: {} TiDB: {} TiKV: {}".format(cluster['cluster_id'],
                                                                                             cluster['project_id'],
                                                                                             cluster['tenant_id'],
                                                                                             components['tidb'],
                                                                                             components['tikv'],
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


