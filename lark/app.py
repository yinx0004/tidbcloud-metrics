import sys

import requests
import json
from openpyxl.utils import get_column_letter
from utils import logger


class LarkApp(object):
    def __init__(self, conf):
        self.conf = conf
        self.headers_without_auth = {'Content-Type': 'application/json;charset=utf-8'}
        #self.redirect_url = "https://open.feishu.cn/api-explorer/cli_a55da5ed2a74d00c"
        #self.redirect_url = "https://127.0.0.1/mock"
        self.redirect_url = "https%3A%2F%2F127.0.0.1%2Fmock"
        self.logger = logger.setup_logger(__name__, conf['logging']['file_name'], conf['logging']['level'])
        self.write_spreadsheet_url = "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{}/values".format(self.conf['lark']['spreadsheet_token'])

        #self.headers = {'Authorization': 'Bearer {}'.format(self.get_user_access_token()),
         #               'Content-Type': 'application/json;charset=utf-8'}

    def get_app_access_token(self):
        url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
        payload = json.dumps({
                    'app_id': self.conf['lark']['app_id'],
                    'app_secret': self.conf['lark']['app_secret']
                   })
        response = requests.request("POST", url, headers=self.headers_without_auth, data=payload)
        if response.status_code == 200:
            return response.json()['app_access_token']
        else:
            self.logger.error("Get Lark app token failed: {}".format(response.json()['msg']))
            sys.exit(1)

    def get_tenant_access_token(self):
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = json.dumps({
                    'app_id': self.conf['lark']['app_id'],
                    'app_secret': self.conf['lark']['app_secret']
                   })
        response = requests.request("POST", url, headers=self.headers_without_auth, data=payload)
        token = response.json()['tenant_access_token']
        if response.status_code == 200:
            self.logger.debug("tenant token: {}".format(token))
            return token
        else:
            self.logger.error("Get Lark tenant access token failed: {}".format(response.json()['msg']))
            sys.exit(1)

    def get_auth_code(self):
        #url = "https://open.feishu.cn/open-apis/authen/v1/authorize?app_id={}&redirect_uri={}&scope={}".format(self.conf['lark']['app_id'], self.redirect_url, "sheets:spreadsheet")
        url = "https://open.feishu.cn/open-apis/authen/v1/authorize?app_id={}&redirect_uri={}&scope={}".format(self.conf['lark']['app_id'], self.redirect_url, "sheets:spreadsheet")
        response = requests.request("GET", url)
        self.logger.debug("get auth code response: {}".format(response))
        if response.history:
            for history in response.history:
                print(history.url)
        #if response.status_code == 200:
        #    print(response.history)
        #    code = response.json()['code']
        #    self.logger.debug("auth code: {}".format(code))
        #    return code
        #else:
        #    self.logger.error("Get Lark auth code failed: {}".format(response.json()['msg']))
        #    sys.exit(1)

    def get_user_access_token(self):
        url = "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token"

        headers = {'Authorization': 'Bearer {}'.format(self.get_app_access_token()),
                                  'Content-Type': 'application/json;charset=utf-8'}

        payload = json.dumps({
            "grant_type": "authorization_code",
            "code": self.get_auth_code()
        })

        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code == 200:
            user_access_token = response.json()
            self.logger.debug("app access token: {}".format(user_access_token))
            return user_access_token
        else:
            self.logger.error("Get Lark user access token failed: {}".format(response.json()['msg']))
            sys.exit(1)

    def write_sheet(self, value):
        rows = len(value)
        columns = len(value[0])
        range_str = 'A1:{}{}'.format(get_column_letter(columns), rows)
        payload = json.dumps({
                "valueRange": {
                    "range": "{}!{}".format(self.conf['lark']['sheet_id'], range_str),
                    "values": value
                    }
                })

        #user_access_token = self.get_user_access_token()
        #headers = {'Authorization': 'Bearer {}'.format(user_access_token),
        #                'Content-Type': 'application/json;charset=utf-8'}

        #tenant_access_token = self.get_tenant_access_token()
        #headers = {'Authorization': 'Bearer {}'.format(tenant_access_token),
        #headers = {'Authorization': 'Bearer {}'.format(self.conf['lark']['tenant_access_token']),
        headers = {'Authorization': 'Bearer {}'.format(self.conf['lark']['user_access_token']),
                              'Content-Type': 'application/json;charset=utf-8'}
        self.logger.debug("payload: {}".format(payload))
        response = requests.request("PUT", self.write_spreadsheet_url, headers=headers, data=payload)
        print(response.text)



