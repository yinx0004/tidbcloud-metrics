from utils import logger


class MetricsAnalyzer:
    def __init__(self, request, resource_usage_metrics, capacity, instance_cnt, conf):
        self.conf = conf
        self.logger = logger.setup_logger(__name__, self.conf['log_file_name'], conf['log_level'])
        self.request = request
        self.resource_usage_metrics = resource_usage_metrics
        self.capacity = capacity
        self.instance_cnt = instance_cnt

    def analyze(self):
        if self.resource_usage_metrics is not None:
            data = {"component": "{}".format(self.request['component']),
                   "name": "{}".format(self.request['name'])}

            for key, value in self.resource_usage_metrics.items():
                data[key] = value

            data["capacity"] = self.capacity
            data["instance_cnt"] = self.instance_cnt

            plan = self.get_resource_capacity_plan(self.instance_cnt, self.capacity)
            if plan is not None:
                for k, v in plan.items():
                    data[k] = v

            return data

    def get_resource_capacity_plan(self, instance_cnt, capacity):
        plan = {}
        for k, v in self.resource_usage_metrics.items():
            key = "plan_{}".format(k)
            plan[key] = self.conf['capacity_plan_traffic_x'] * self.conf['capacity_plan_resource_redundancy_x'] * v.item() * instance_cnt / int(capacity)
        return plan
