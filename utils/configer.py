from utils import helpers
import datetime


class Configer:
    def __init__(self, config_file, end_time):
        self.config_file = config_file
        self.end_time = end_time
        self.conf = {
            "log_level": "INFO",
            "log_to_file": False,
            "log_file_name": None,
            "prometheus_start_time": self.end_time - datetime.timedelta(days=1),
            "prometheus_end_time": self.end_time,
            "prometheus_step_in_seconds": "60s",
            "prometheus_cluster_prom_base_url": None,
            "prometheus_cluster_prom_id_token": None,
            "prometheus_k8s_prom_base_url": None,
            "capacity_plan_traffic_x": 2,
            "capacity_plan_resource_redundancy_x": 2,
            "capacity_plan_cpu_usage_goal": 10,
        }

    def set_conf(self):

        yaml_data = helpers.parse_yaml(self.config_file)

        # validate longging
        helpers.validate_logging_level(yaml_data["logging"]["level"], 'logging.level', allow_none=True)
        if yaml_data["logging"]["level"] is not None:
            self.conf["log_level"] = yaml_data["logging"]["level"].upper()

        helpers.validate_boolean(yaml_data["logging"]["to_file"], 'logging.to_file', allow_none=True)
        if yaml_data["logging"]["to_file"] is not None:
            self.conf["log_to_file"] = yaml_data["logging"]["to_file"]

        # validate prometheus
        helpers.validate_non_empty_string(yaml_data["prometheus"]["start_time"], 'prometheus.start_time', allow_none=True)
        if yaml_data["prometheus"]["start_time"] is not None:
            self.conf["prometheus_start_time"] = yaml_data["prometheus"]["start_time"]

        helpers.validate_non_empty_string(yaml_data["prometheus"]["end_time"], 'prometheus.end_time', allow_none=True)
        if yaml_data["prometheus"]["end_time"] is not None:
            self.conf["prometheus_end_time"] = yaml_data["prometheus"]["end_time"]

        helpers.validate_non_empty_string(yaml_data["prometheus"]["step_in_seconds"], 'prometheus.step_in_seconds', allow_none=True)
        if yaml_data["prometheus"]["step_in_seconds"] is not None:
            self.conf["prometheus_step_in_seconds"] = yaml_data["prometheus"]["step_in_seconds"]

        helpers.validate_non_empty_string(yaml_data["prometheus"]["cluster_prom_base_url"], 'prometheus.cluster_prom_base_url', allow_none=False)
        self.conf["prometheus_cluster_prom_base_url"] = yaml_data["prometheus"]["cluster_prom_base_url"]

        helpers.validate_non_empty_string(yaml_data["prometheus"]["cluster_prom_id_token"], 'prometheus.cluster_prom_id_token', allow_none=False)
        self.conf["prometheus_cluster_prom_id_token"] = yaml_data["prometheus"]["cluster_prom_id_token"]

        helpers.validate_int(yaml_data["capacity"]["plan_traffic_x"], 'capacity.plan_traffic_x', allow_none=True)
        if yaml_data["capacity"]["plan_traffic_x"] is not None:
            self.conf["capacity_plan_traffic_x"] = yaml_data["capacity"]["plan_traffic_x"]

        helpers.validate_int(yaml_data["capacity"]["plan_resource_redundancy_x"], 'capacity.plan_resource_redundancy_x', allow_none=True)
        if yaml_data["capacity"]["plan_resource_redundancy_x"] is not None:
            self.conf["capacity_plan_resource_redundancy_x"] = yaml_data["capacity"]["plan_resource_redundancy_x"]

        helpers.validate_int(yaml_data["capacity"]["plan_cpu_usage_goal"], 'capacity.plan_cpu_usage_goal', allow_none=True)
        if yaml_data["capacity"]["plan_cpu_usage_goal"] is not None:
            self.conf["capacity_plan_cpu_usage_goal"] = yaml_data["capacity"]["plan_cpu_usage_goal"]

        return self.conf
