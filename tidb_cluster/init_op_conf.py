from utils import helpers
from datetime import datetime

class TidbOpConfig:
    def __init__(self, config_file):
        """
        初始化 TidbOpConfig 类，加载配置文件并将其封装为类的属性。
        """
        self.config_file = config_file
    
    def set_conf(self):
        self.conf = helpers.parse_yaml(self.config_file).get('tidbop')
        self.conf['time'] = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        # validate auth
        helpers.validate_non_empty_string(
            self.conf['metrics_api_url'],
            'tidbop.metrics_api_url',
            allow_none=False)
               
        return self.conf