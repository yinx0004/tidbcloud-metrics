from datetime import datetime
from utils import logger
from utils.configer import Configer
from capacity_planner.capacity_planner import CapacityPlanner


def get_tidb_cluster_info(prometheus_cluster_prom_base_url):
    info = prometheus_cluster_prom_base_url.split("/")
    cluster_info = {
        'ds_domain': info[2],
        'tenant_id': info[7],
        'project_id': info[9],
        'cluster_id': info[-1],
    }
    domain_info = cluster_info['ds_domain'].split('.')
    cluster_info['region'] = domain_info[2]
    cluster_info['cloud_provider'] = domain_info[3]
    cluster_info['k8s_cluster'] = 'prod-{}-eks-{}-.*'.format(cluster_info['project_id'], cluster_info['region'])

    return cluster_info


if __name__ == '__main__':
    now = datetime.now()
    # get configurations
    conf = Configer("tidbcloud.yaml", now).set_conf()
    cluster_info = get_tidb_cluster_info(conf['prometheus_cluster_prom_base_url'])

    # setup logging
    if conf['log_to_file']:
        conf['log_file_name'] = "logs/{}_{}.log".format(cluster_info['cluster_id'], now.strftime("%Y-%m-%d-%H-%M-%S"))
    logger = logger.setup_logger(__name__, conf['log_file_name'], conf['log_level'])
    logger.debug("test")

    capacity_planner = CapacityPlanner(conf, cluster_info, 'node')
    capacity_planner.generate_capacity_plan()



