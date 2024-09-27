import sys
import datetime
from health_checker.health_checker import HealthChecker
from utils.logger import setup_logger
from tidb_cluster.configer import Configer
from capacity_planner.capacity_planner import CapacityPlanner
from tidb_cluster.tidb_cluster import TiDBCluster
import click
from lark.app import LarkApp



if __name__ == '__main__':
    conf = Configer("tidbcloud.yaml").set_conf()
    # logger = setup_logger(__name__, conf['logging']['file_name'], conf['logging']['level'])
    # tidb_cluster = TiDBCluster(conf)
    # print(tidb_cluster.get_dedicated_clusters_by_tenant_from_k8s())