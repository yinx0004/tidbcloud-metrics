from utils import helpers
import datetime
import requests
from urllib import parse


class Configer:

    def __init__(self, config_file):
        self.config_file = config_file
        self.now = datetime.datetime.now()
        self.conf = None
        self.default_conf = {
            'logging': {
                'level': 'INFO',
                'dir': 'logs'
            },
            'prometheus': {
                'start_time': self.now - datetime.timedelta(days=1),
                'end_time': self.now,
                'step_in_seconds': '60s',
                'cluster_prom_base_url': None,
                'cluster_prom_id_token': None,
                'k8s_prom_base_url': None
            },
            'capacity': {
                'plan_traffic_x': 2,
                'plan_resource_redundancy_x': 2,
                'plan_cpu_usage_goal': 10
            },
        }

    def set_conf(self):
        self.conf = helpers.parse_yaml(self.config_file)

        self.conf['time'] = self.now.strftime("%Y-%m-%d-%H-%M-%S")
        # validate auth
        helpers.validate_non_empty_string(
            self.conf['prometheus']['cluster_prom_base_url'],
            'prometheus.cluster_prom_base_url',
            allow_none=False)

        helpers.validate_non_empty_string(
            self.conf['prometheus']['cluster_prom_id_token'],
            'prometheus.cluster_prom_id_token',
            allow_none=False)

        # validate logging
        helpers.validate_logging_level(self.conf['logging']['level'],
                                       'logging.level',
                                       allow_none=True)
        if self.conf['logging']['level'] is not None:
            self.conf['logging']['level'] = self.conf['logging'][
                'level'].upper()
        else:
            self.conf['logging']['level'] = self.default_conf['logging'][
                'level']

        helpers.validate_non_empty_string(self.conf['logging']['dir'],
                                          'logging.dir',
                                          allow_none=True)
        if self.conf['logging']['dir'] is None:
            self.conf['logging']['dir'] = self.default_conf['logging']['dir']

        self.conf['cluster_info'] = self.get_tidb_cluster_info()
        self.conf['logging']['file_name'] = "{}/{}_{}.log".format(
            self.conf['logging']['dir'],
            self.conf['cluster_info']['cluster_id'], self.conf['time'])

        self.conf['prometheus'][
            'k8s_prom_base_url'] = "https://www.ds.{}.aws.observability.tidbcloud.com/internal/metrics/d5d1a915-1d37-22a7-82b8-8cb67cc57820".format(
                self.conf['cluster_info']['region'])

        # # validate prometheus
        helpers.validate_non_empty_string(
            self.conf['prometheus']['start_time'],
            'prometheus.start_time',
            allow_none=True)
        if self.conf['prometheus']['start_time'] is None:
            self.conf['prometheus']['start_time'] = self.default_conf[
                'prometheus']['start_time']

        helpers.validate_non_empty_string(self.conf['prometheus']['end_time'],
                                          'prometheus.end_time',
                                          allow_none=True)
        if self.conf['prometheus']['end_time'] is None:
            self.conf['prometheus']['end_time'] = self.default_conf[
                'prometheus']['end_time']

        helpers.validate_non_empty_string(
            self.conf['prometheus']['step_in_seconds'],
            'prometheus.step_in_seconds',
            allow_none=True)
        if self.conf['prometheus']['step_in_seconds'] is None:
            self.conf['prometheus']['step_in_seconds'] = self.default_conf[
                'prometheus']['step_in_seconds']
        
        self.get_token_from_tidbcloudapi()
        # print(self.conf['prometheus']['cluster_prom_id_token'])
        # self.conf['prometheus']['cluster_prom_id_token'] = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlJEWTNNVUpGTUVReU9VVTBSa0U1TXpCRk5rRkRRVEl3UkRNMU0wSXpNelJHUVRrMVFUbEZRZyJ9.eyJodHRwczovL3RpZGJjbG91ZC5jb20vbGFzdF9wYXNzd29yZF9yZXNldCI6IjIwMjQtMDctMThUMTI6MjY6NTYuMjA1WiIsImh0dHBzOi8vdGlkYmNsb3VkLmNvbS9sb2dpbl9yZWNlaXZlZF9hdCI6MTcyMjI0OTkzMDQ0NSwibG9naW5faGFzX29yZyI6IjEiLCJsb2dpbl9vcmdfdHlwZSI6InBlcnNvbmFsIiwibG9naW5fb3JnX2lkIjoiMSIsImxvZ2luX2NvbXBhbnlfbmFtZSI6IiIsImVtYWlsIjoieXVlY2hhbmdxaWFuZ0BwaW5nY2FwLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJpc3MiOiJodHRwczovL3RpZGIuYXV0aDAuY29tLyIsImF1ZCI6IjZJWnRoQ2ZtUktJUEVuUVNUOGFEYnRNN1NHZE1uaVJsIiwiaWF0IjoxNzIyMjQ5OTMwLCJleHAiOjE3MjIyODU5MzAsInN1YiI6ImF1dGgwfDYxY2E3MzY4ZTk1Njc1MDA2ODJhZDE4MiIsImF0X2hhc2giOiJFc1pBQlI3SmhXQ01GMXczckg4b1pBIiwic2lkIjoiX3QtX3F2bFJRTUZZM0xaWHVlb1hEXzQ3N3FQWl90MUkiLCJub25jZSI6ImZoRkdsS1BqRFNWWW94WVdLR0VHQnd2VWtpd0ZXWXVRIn0.OKhnKtxk9SOC0ramehRb_BnRKUWrzB4cYrwZid3uv9yWaCph7gMA7iIufT0G-5HCAF5tOQCMKNIviczssvAEGOqC5qLu0dCBpIN4swaQpp6g4uTSo2lUlkI_9Ed9QTlCfKvsqH7apG4OGYMYK0s3XP7KRaPTmT5Azv6dl-7Y9u-RqOdzpvRcbo7DkT8CnFPNDTzPiuocPAFZ-DQei-QLfTZSU12hBw1D4wCuazxv29qL32rBEDeGyjFFQwPhJ5R3WhKlgyX-Aj0sE7L453ZQgWzL7OPKvieqE1WI-wCO2PuwOAuGw-8GaW7R5cMT-X5KRd4B134FI4rEKmxj_w9vGA'
        return self.conf

    def get_token_from_tidbcloudapi(self):

        # self.conf = helpers.parse_yaml(self.config_file)
        helpers.validate_non_empty_string(
            self.conf['tidbcloud']['authenticate_url'],
            'authenticate_url',
            allow_none=False)
        helpers.validate_non_empty_string(self.conf['tidbcloud']['username'],
                                          'authenticate_url',
                                          allow_none=False)
        helpers.validate_non_empty_string(self.conf['tidbcloud']['password'],
                                          'authenticate_url',
                                          allow_none=False)

        tidbcloud_url = self.conf['tidbcloud']['authenticate_url']
        headers_api_one = {"Origin": "https://tidbcloud.com"}
        body_api_one = {
            "username": self.conf['tidbcloud']['username'],
            "password": self.conf['tidbcloud']['password'],
            "client_id": "6IZthCfmRKIPEnQST8aDbtM7SGdMniRl",
            "credential_type":
            "http://auth0.com/oauth/grant-type/password-realm",
            "realm": "custom-email",
        }
        response_api_one = requests.post(tidbcloud_url,
                                         json=body_api_one,
                                         headers=headers_api_one)
        if response_api_one.status_code == 200:
            # {'login_ticket': 'W8hqXNyx_0KIg9Y_HFXbUWtfp8H8vesz', 'co_verifier': 'vv_XF9O99kSXbv8Qw1fsrXUaLtpdpiWh', 'co_id': 'NPASB21Zsbhi'}
            # print(response.json())

            # 检查响应中的 Set-Cookie 头部信息
            if 'Set-Cookie' in response_api_one.headers:
                cookies = response_api_one.headers['Set-Cookie']
            else:
                print("No cookies found in the response headers")
            
            

            headers_api_two = {"Cookie": helpers.extract_and_combine(cookies,['auth0','auth0_compat','did','did_compat'])}
            body_api_two = {
                "login_ticket":
                response_api_one.json().get('login_ticket'),
                "client_id":
                '6IZthCfmRKIPEnQST8aDbtM7SGdMniRl',
                "response_type":
                parse.quote("token id_token"),
                "redirect_uri":
                parse.quote_plus("https://tidbcloud.com/auth_redirect"),
                "scope":
                parse.quote("openid email"),
                "realm":
                "custom-email",
                "state":
                helpers.generate_random_string(32),
                "nonce":
                helpers.generate_random_string(32),
                "auth0Client":
                "eyJuYW1lIjoiYXV0aDAuanMiLCJ2ZXJzaW9uIjoiOS4xOS4xIn0"
            }
            # eyJuYW1lIjoiYXV0aDAuanMiLCJ2ZXJzaW9uIjoiOS4xOS4xIn0
            params = helpers.escape_space("&".join([f"{key.replace(':', '=')}={value}" for key, value in body_api_two.items()]))
            # params = parse.urlencode(body_api_two)
            url="https://tidb.auth0.com/authorize?"+params
            # print("curl \'" + url + "\' --header \'Cookie: "+ headers_api_two.get("Cookie")+"\'")
            # response_api_two = requests.get("https://tidb.auth0.com/authorize",params=body_api_two,
            #             headers=headers_api_two,allow_redirects=False)
            response_api_two = requests.get(url=url,
                        headers=headers_api_two,allow_redirects=False)
        
            if response_api_two.status_code == 302:
                self.conf['prometheus']['cluster_prom_id_token'] = helpers.extract_id_token(response_api_two.text,"id_token=","&")
            else:
                print(
                    f"tidbcloud API Two Get request failed with status code: {response_api_two.text}"
                )

        else:
            print(
                f"tidbcloud API One POST request failed with status code: {response_api_one.json()}"
            )

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
        cluster_info['k8s_cluster'] = 'prod-{}-eks-{}-.*'.format(
            cluster_info['project_id'], cluster_info['region'])

        return cluster_info
