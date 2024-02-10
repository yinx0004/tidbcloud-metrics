from utils import logger


class CapacityPlanner:
    def __init__(self, metrics, plan_traffic_x, plan_resource_redundancy_x, log_file_name, log_level):
        self.metrics = metrics
        self.plan_traffic_x = plan_traffic_x
        self.plan_resource_redundancy_x = plan_resource_redundancy_x
        self.logger = logger.setup_logger(__name__, log_file_name, log_level)

    def get_resource_capacity_plan(self, instance_cnt, capacity):
        plan = {}
        for k, v in self.metrics.items():
            key = "plan_{}".format(k)
            plan[key] = self.plan_traffic_x * self.plan_resource_redundancy_x * v.item() * instance_cnt / int(capacity)
        return plan
