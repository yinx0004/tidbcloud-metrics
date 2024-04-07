from utils import logger


class MetricsAnalyzer:
    def __init__(self, request, resource_usage_metrics, capacity, instance_cnt, conf):
        self.conf = conf
        self.logger = logger.setup_logger(__name__, self.conf['logging']['file_name'], self.conf['logging']['level'])
        self.request = request
        self.resource_usage_metrics = resource_usage_metrics
        self.capacity = capacity
        self.instance_cnt = instance_cnt

    #def analyze(self):
    #    if self.resource_usage_metrics is not None:
    #        data = {"component": "{}".format(self.request['component']),
    #               "name": "{}".format(self.request['name'])}

    #        for key, value in self.resource_usage_metrics.items():
    #            data[key] = value

    #        data["capacity"] = self.capacity
    #        data["instance_cnt"] = self.instance_cnt

    #        plan = self.get_resource_capacity_plan(self.instance_cnt, self.capacity)
    #        if plan is not None:
    #            for k, v in plan.items():
    #                data[k] = v

    #        return data

    def analyze(self):
        if self.resource_usage_metrics is not None:
            data = {"component": "{}".format(self.request['component']),
                   "name": "{}".format(self.request['name'])}

            for key, value in self.resource_usage_metrics.items():
                data[key] = value

            data["capacity"] = self.capacity
            data["instance_cnt"] = self.instance_cnt

            if self.request['component'] == 'tidb' and self.request['name'] == 'Memory(byte)':
                plan = self.get_tidb_mem_resource_capacity_plan(self.instance_cnt, self.capacity)
            else:
                plan = self.get_resource_capacity_plan(self.instance_cnt, self.capacity)
            if plan is not None:
                for k, v in plan.items():
                    data[k] = v

            return data
        else:
            return None

    def get_resource_capacity_plan(self, instance_cnt, capacity):
        plan = {}
        for k, v in self.resource_usage_metrics.items():
            key = "plan_{}".format(k)
            plan[key] = self.conf['capacity']['plan_traffic_x'] * self.conf['capacity']['plan_resource_redundancy_x'] * v.item() * instance_cnt / int(capacity)
        return plan

    #def get_tidb_mem_resource_capacity_plan(self, instance_cnt, capacity):
    #    # （(瓶颈资源使用量（max） / 0.9 / 0.8) * 业务量倍数 * 资源冗余 + 5.5GB）* 当前节点数 / 单节点瓶颈资源容量上限 = 预估节点数
    #    #  资源冗余：内存推荐值为 1.3
    #    plan = {}
    #    for k, v in self.resource_usage_metrics.items():
    #        key = "plan_{}".format(k)
    #        plan[key] = (v.item() / 0.9 / 0.8 * self.conf['capacity']['plan_traffic_x'] * 1.3 + 5.5 * 1024 * 1024 * 1024) * instance_cnt / int(capacity)
    #    return plan

    def get_tidb_mem_resource_capacity_plan(self, instance_cnt, capacity):
        # （瓶颈资源使用量（max）  * 业务量倍数 * 资源冗余 ）* 当前节点数 / (单节点瓶颈资源容量上限 - 5.5G系统消耗） = 预估节点数
        #  资源冗余：内存推荐值为 1.3
        plan = {}
        for k, v in self.resource_usage_metrics.items():
            key = "plan_{}".format(k)
            plan[key] = self.conf['capacity']['plan_traffic_x'] * self.conf['capacity']['plan_resource_redundancy_x'] * v.item() * instance_cnt / (int(capacity) - 5.5 * 1024 * 1024 * 1024)
        return plan