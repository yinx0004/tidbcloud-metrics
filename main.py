from health_checker.health_checker import HealthChecker
from utils.logger import setup_logger
from utils.configer import Configer
from capacity_planner.capacity_planner import CapacityPlanner
import click

# consts
health_check_type = ["all", "tidb", "tikv", "pd", "tiflash"]


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
    health_checker = HealthChecker(conf, health_check_type)
    health_checker.check_health(type, report)


if __name__ == '__main__':
    conf = Configer("tidbcloud.yaml").set_conf()
    logger = setup_logger(__name__, conf['logging']['file_name'], conf['logging']['level'])
    cli()


