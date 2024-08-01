import os
import json
import locale
import logging
import hashlib
import requests
from datetime import datetime

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class API_Requests(object):
    def __init__(self, api_credentials:dict = None) -> None:
        self.api_credentials = api_credentials
        self.ip = self.api_credentials['ip']
        self.port = self.api_credentials['port']
        self.http = self.api_credentials['http']
        self.email = self.api_credentials['email']
        self.password = self.api_credentials['password']
        self.salt = self.api_credentials['salt']

        self.weekdays = ['Maandag', 'Dinsdag', 'Woensdag', 'Donderdag', 'Vrijdag', 'Zaterdag', 'Zondag']
        self.months = ['', 'Januari', 'Februari', 'Maart', 'April', 'Mei', 'Juni', 'Juli', 'Augustus', 'September', 'Oktober', 'November', 'December']
        pass

    def get_bearer_key(self)->str:
        try:
            payload = json.dumps({"email": self.email, "password": self.get_hashed_password()})
            reqUrl = f"{self.http}://{self.ip}:{self.port}/energy/api/v1.0/login"
            headersList = {
            "Accept": "*/*",
            "User-Agent": "Thunder Client (https://www.thunderclient.com)",
            "Content-Type": "application/json"
            }
            response = requests.request("POST", reqUrl, data=payload,  headers=headersList, timeout=5)
            if response.status_code == 200:
                mjson = response.json()
                return mjson['access_token']
            return False
        except Exception as e:
            log.critical(e, exc_info=True)

    def get_hashed_password(self)->str:
        try:
            if self.password is None or self.salt is None:
                raise Exception('Geen wachtwoord of salt?')

            # Adding salt at the last of the password
            salted_password = self.password+self.salt
            # Encoding the password
            hashed_password = hashlib.md5(salted_password.encode())

            return hashed_password.hexdigest()
        except Exception as e:
            log.critical(e, exc_info=True)

    @staticmethod
    def dutch_floats(price:float = None, my_locale:str="nl_NL")->str:
        if my_locale is None or my_locale == "":
            my_locale = "nl_NL"

        my_locale = f"{my_locale}.UTF-8"

        try:
            locale.setlocale(locale.LC_ALL, my_locale)
        except Exception as e:
            log.error(f"{my_locale}: {e}", exc_info=True)
            my_locale = "nl_NL.UTF-8"
            locale.setlocale(locale.LC_ALL, my_locale)

        try:
            if price is None or price == "":
                return ""

            return locale.format_string("€ %.3f", price, grouping=False)

        except (KeyError,Exception) as e:
            log.error(e, exc_info=True)
            return False

    @staticmethod
    def prijs_instelling_tekst(instelling="k")->str:
        match instelling:
            case 'k':
                return "Kaal (Inkoop)"
            case 'o':
                return "Inkoop+opslag+BTW "
            case 'a':
                return "All-In "
            case _:
                return "Kaal (Inkoop)"

    @staticmethod
    def next_hour(hour:str= None)->str:
        try:
            if hour is None:
                raise Exception('Geen uur mee gegeven')
            int_hour = int(hour[:2]) + 1
            return f"{int_hour:02d}:00"
        except Exception as e:
            log.error(e, exc_info=True)

    @staticmethod
    def login_hash(user_id:int, user_salt:str, login_secret:str):
        # php -> echo hash('sha512', 'foo');
        # hashlib.sha512(b'foo').hexdigest()
        hash_string = bytes(f"{user_id}-{user_salt}-{login_secret}", encoding='utf-8')
        hash = hashlib.sha512(hash_string).hexdigest()
        return f"{user_id}-{hash}:{user_salt}"

    def get_nice_day(self, date:str = None, weekday:bool = False) -> str:
        try:
            if date is None:
                vandaag_ts = datetime.now()
                date = vandaag_ts.strftime("%Y-%m-%d")

            date = f"{date} 01:01:01"
            dt = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

            day = dt.strftime("%d")
            year = dt.strftime("%Y")
            weekday = self.weekdays[dt.weekday()]
            month_int = int(dt.strftime("%m"))
            month = self.months[month_int]

            if weekday:
                return f"{weekday} {day} {month} {year}"
            else:
                return f"{day} {month} {year}"

        except Exception as e:
            log.error(e, exc_info=True)