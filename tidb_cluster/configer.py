from utils import helpers
import datetime


class Configer:
    def __init__(self, config_file):
        self.config_file = config_file
        self.now = datetime.datetime.now()
        self.conf = None
        self.default_conf = {
            'logging': {'level': 'INFO', 'dir': 'logs'},
            'prometheus': {'start_time': self.now - datetime.timedelta(days=1),
                            'end_time': self.now,
                            'step_in_seconds': '60s',
                            'cluster_prom_base_url': None,
                            'cluster_prom_id_token': None,
                            'k8s_prom_base_url': None},
            'capacity': {'plan_traffic_x': 2, 'plan_resource_redundancy_x': 2, 'plan_cpu_usage_goal': 10},
        }

    def set_conf(self):
        self.conf = helpers.parse_yaml(self.config_file)

        self.conf['time'] = self.now.strftime("%Y-%m-%d-%H-%M-%S")
        # validate auth
        helpers.validate_non_empty_string(self.conf['prometheus']['cluster_prom_base_url'],
                                          'prometheus.cluster_prom_base_url', allow_none=False)

        helpers.validate_non_empty_string(self.conf['prometheus']['cluster_prom_id_token'],
                                          'prometheus.cluster_prom_id_token', allow_none=False)

        # validate logging
        helpers.validate_logging_level(self.conf['logging']['level'], 'logging.level', allow_none=True)
        if self.conf['logging']['level'] is not None:
            self.conf['logging']['level'] = self.conf['logging']['level'].upper()
        else:
            self.conf['logging']['level'] = self.default_conf['logging']['level']

        helpers.validate_non_empty_string(self.conf['logging']['dir'], 'logging.dir', allow_none=True)
        if self.conf['logging']['dir'] is None:
            self.conf['logging']['dir'] = self.default_conf['logging']['dir']

        self.conf['cluster_info'] = self.get_tidb_cluster_info()
        self.conf['logging']['file_name'] = "{}/{}_{}.log".format(self.conf['logging']['dir'], self.conf['cluster_info']['cluster_id'],
                                                             self.conf['time'])

        self.conf['prometheus']['k8s_prom_base_url'] = "https://www.ds.{}.aws.observability.tidbcloud.com/internal/metrics/d5d1a915-1d37-22a7-82b8-8cb67cc57820".format(self.conf['cluster_info']['region'])

        # # validate prometheus
        helpers.validate_non_empty_string(self.conf['prometheus']['start_time'], 'prometheus.start_time', allow_none=True)
        if self.conf['prometheus']['start_time'] is None:
            self.conf['prometheus']['start_time'] = self.default_conf['prometheus']['start_time']

        helpers.validate_non_empty_string(self.conf['prometheus']['end_time'], 'prometheus.end_time', allow_none=True)
        if self.conf['prometheus']['end_time'] is None:
            self.conf['prometheus']['end_time'] = self.default_conf['prometheus']['end_time']

        helpers.validate_non_empty_string(self.conf['prometheus']['step_in_seconds'], 'prometheus.step_in_seconds', allow_none=True)
        if self.conf['prometheus']['step_in_seconds'] is None:
            self.conf['prometheus']['step_in_seconds'] = self.default_conf['prometheus']['step_in_seconds']

        return self.conf

    def get_tidb_cluster_info(self):
        info = self.conf['prometheus']['cluster_prom_base_url'].split("/")
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
