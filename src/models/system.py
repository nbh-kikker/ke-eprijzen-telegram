import os
import json
import logging
import requests

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

from models.api_requests import API_Requests

class API_System(API_Requests):
    def __init__(self,*args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def _get_sys_info(self)->dict:
        reqUrl = f"http://{self.api_credentials['ip']}:{self.api_credentials['port']}/energy/api/v1.0/system"
        headersList = {
        "Accept": "*/*",
        "User-Agent": "Thunder Client (https://www.thunderclient.com)",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {self.api_credentials['bearer_key']}"
        }
        response = requests.request("GET", reqUrl, headers=headersList, timeout=2)
        if response.status_code == 200:
            return response.json()
        return None