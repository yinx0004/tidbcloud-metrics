import requests
import time
import utils.helpers

class AI:
    def __init__(self):
        self.post_url = "https://linguflow.pingcap.net/linguflow-api/applications/55efc784-160e-49fd-afa5-f91b80eee96f/async_run?application_id=55efc784-160e-49fd-afa5-f91b80eee96f"
        self.get_url = "https://linguflow.pingcap.net/linguflow-api"
        self.timeout = 100

    def post_request(self,request_input):

        input={'input':request_input}
        res=requests.post(url=self.post_url,json=input,verify=False,headers={'x-linguflow-access-key':'654b5c8a8860c40200dfb836','x-linguflow-access-secret':'f117aab6a2180c4424be069d645022b4','x-linguflow-user':'xq'})
        if res.status_code == 200:
            return res.json()
        else:
            return "ERROR: {}".format(res.json())

    def get_data_with_retry(self,input_id):
        self.get_url=self.get_url+"/interactions/{}".format(input_id['id'])
        print(self.get_url)
        start_time = time.time()
        while time.time() - start_time < self.timeout:

            response = requests.get(self.get_url,verify=False,headers={'x-linguflow-access-key':'654b5c8a8860c40200dfb836','x-linguflow-access-secret':'f117aab6a2180c4424be069d645022b4','x-linguflow-user':'xq'})
            if response.status_code == 200 and response.json().get('interaction') is not None:
                output = response.json().get('interaction').get('output')
                if output is not None:
                    return utils.helpers.formatOutput(output)
            time.sleep(2)  # 等待1秒后重试
        raise ValueError("Error: Timeout reached. Unable to fetch data within {}s. response is {}".format(self.timeout,response.json()))
