import os
import json
import logging
import requests

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

from models.api_requests import API_Requests

class API_users(API_Requests):
    def __init__(self,*args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def _add_user(self, user_id:int = None)->int:
        try:
            payload = json.dumps({
                    "datetime": None,
                    "kaal_opslag_allin": None,
                    "ochtend": None,
                    "middag": None,
                    "opslag_electra": None,
                    "opslag_gas": None,
                    "melding_lager_dan": None,
                    "ode_gas": None,
                    "ode_electra": None,
                    "eb_electra": None,
                    "eb_gas": None,
                    "country": "NL",
                    "locale": "de_DE"
                    })
            return self._api_call_get_add_user(user_id=user_id, payload=payload, call="PUT")
        except Exception as e:
            log.error(e, exc_info=True)
            return False

    def _get_user_by_id(self, user_id:int = None)->dict:
        try:
            return self._api_call_get_add_user(user_id=user_id, call="GET")
        except Exception as e:
            log.error(e, exc_info=True)
            return {}

    def _get_users(self)->list:
        try:
            reqUrl = f"http://{self.api_credentials['ip']}:{self.api_credentials['port']}/energy/api/v1.0/users"
            headersList = {
            "Accept": "*/*",
            "User-Agent": "Thunder Client (https://www.thunderclient.com)",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_credentials['bearer_key']}"
            }
            response = requests.request("GET", reqUrl, headers=headersList, timeout=3)
            if response.status_code == 200:
                return response.json()
            if response.status_code == 404:
                #niet gevonden
                return None
            return None
        except Exception as e:
            log.error(e, exc_info=True)
            return False

    def _get_user_ids(self)->list:
        try:
            users_data = self._api_call_get_add_user()
            users = users_data['data']

            return [user['user_id'] for user in users]

        except Exception as e:
            log.error(e, exc_info=True)
            return False

    def _remove_user(self, user_id:int = None)->bool:
        try:
            return self._api_call_get_add_user(user_id=user_id, call="DELETE")
        except Exception as e:
            log.error(e, exc_info=True)
            return False

    def _get_ochtend_users(self, hour:int = None)->list:
        try:
            payload = json.dumps({"ochtend": hour})
            return self._api_call_get_add_user(payload=payload)
        except Exception as e:
            log.error(e, exc_info=True)
            return False

    def _set_soortprijs_user(self, user_id:int = None, soort:int = 'k')->bool:
        try:
            payload = json.dumps({"kaal_opslag_allin": soort})
            return self._api_call_update_user(payload=payload,user_id=user_id)
        except Exception as e:
            log.error(e, exc_info=True)
            return False

    def _set_user_value(self, user_id:int = None, data:dict = None)->bool:
        try:
            payload = json.dumps(data)
            return self._api_call_update_user(payload=payload,user_id=user_id)
        except Exception as e:
            log.error(e, exc_info=True)
            return False

    def _set_ochtend_user(self, user_id:int = None, hour:int = 8)->bool:
        try:
            payload = json.dumps({"ochtend": hour})
            return self._api_call_update_user(payload=payload,user_id=user_id)
        except Exception as e:
            log.error(e, exc_info=True)
            return False

    def _set_middag_user(self, user_id:int = None, hour:int = 15)->list:
        try:
            payload = json.dumps({"middag": hour})
            return self._api_call_update_user(payload=payload,user_id=user_id)
        except Exception as e:
            log.error(e, exc_info=True)
            return False

    def _set_user_tokens(self, user_id:int, tokens:int, api_date:str)->list:
        try:
            payload = json.dumps({"api_calls": tokens, "api_valid_date": api_date})
            return self._api_call_update_user(payload=payload,user_id=user_id)
        except Exception as e:
            log.error(e, exc_info=True)
            return False

    def _get_middag_users(self, hour:int = None)->dict:
        try:
            payload = json.dumps({"middag": hour})
            return self._api_call_get_add_user(payload=payload)
        except Exception as e:
            log.error(e, exc_info=True)
            return False

    def _api_call_update_user(self, payload:json=None, user_id:int=None, call:str="PATCH")->json:
        try:
            reqUrl = f"http://{self.api_credentials['ip']}:{self.api_credentials['port']}/energy/api/v1.0/users/{user_id}"

            headersList = {
            "Accept": "*/*",
            "User-Agent": "Thunder Client (https://www.thunderclient.com)",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_credentials['bearer_key']}"
            }
            response = requests.request(call, reqUrl, data=payload, headers=headersList, timeout=3)

            if response.status_code in [201, 200]:
                return response.json()

            if response.status_code == 204: #delete
                return True

            return False #bij niet gevonden!
        except Exception as e:
            log.error(e, exc_info=True)
            return False

    def _api_call_get_add_user(self, payload:json=None, user_id:int=None, call:str="GET")->dict:
        try:
            if user_id is None:
                reqUrl = f"http://{self.api_credentials['ip']}:{self.api_credentials['port']}/energy/api/v1.0/users"
            else:
                reqUrl = f"http://{self.api_credentials['ip']}:{self.api_credentials['port']}/energy/api/v1.0/users/{user_id}"

            headersList = {
            "Accept": "*/*",
            "User-Agent": "Thunder Client (https://www.thunderclient.com)",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_credentials['bearer_key']}"
            }
            if payload is None:
                response = requests.request(call, reqUrl, headers=headersList, timeout=3)
            else:
                response = requests.request(call, reqUrl, data=payload, headers=headersList, timeout=3)

            if response.status_code in [201, 200]:
                return response.json()

            if response.status_code == 204: #delete
                return True

            raise Exception(f"Status {response.status_code}, {response.text}")

        except Exception as e:
            log.error(f"{e}, payload: {payload}, user_id = {user_id}", exc_info=True)
            return False