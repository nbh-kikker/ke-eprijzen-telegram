import os
import json
import logging
import requests

from models.api_requests import API_Requests

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)


class API_prices(API_Requests):
    def __init__(self,*args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def _get_prices(self, datum:str = None, tijd:str = None, kind:str = None, user_id:int = None, lowest:bool = False, highest:bool = False)->dict:
        try:
            payload = json.dumps({"fromdate": datum, "fromtime": tijd, "dutch_floats": False, "kind": kind,
                                  "user_id": user_id, "lowest":lowest, "highest":highest, "country": "NL"})
            return self._api_call(payload=payload)
        except Exception as e:
            log.error(e, exc_info=True)
            return False

    def _api_call(self, payload:json = None)->json:
        try:
            reqUrl = f"http://{self.api_credentials['ip']}:{self.api_credentials['port']}/energy/api/v1.0/prices"
            headersList = {
            "Accept": "*/*",
            "User-Agent": "Thunder Client (https://www.thunderclient.com)",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_credentials['bearer_key']}"
            }
            response = requests.request("GET", reqUrl, data=payload, headers=headersList, timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            log.error(e, exc_info=True)
            return None