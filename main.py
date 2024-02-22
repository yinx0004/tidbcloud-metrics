import sys

from health_checker.health_checker import HealthChecker
from utils.logger import setup_logger
from library.configer import Configer
from capacity_planner.capacity_planner import CapacityPlanner
from library.tidb_cluster import TiDBCluster
import click

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


if __name__ == '__main__':
    conf = Configer("tidbcloud.yaml").set_conf()
    logger = setup_logger(__name__, conf['logging']['file_name'], conf['logging']['level'])
    tidb_cluster = TiDBCluster(conf)
    cli()


