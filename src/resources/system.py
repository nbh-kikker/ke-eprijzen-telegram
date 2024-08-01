import os
import logging

from datetime import datetime

import psutil
from telegram.utils.helpers import escape_markdown

from models.system import API_System

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class System(API_System):
    def __init__(self,*args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def systeminfo_msg(self, version:str=None, seconds:int = None)->str:
        try:
            sys_info = self._get_sys_info()
            vandaag_ts = datetime.now()
            vandaag = vandaag_ts.strftime(("%Y-%m-%d %H:%M"))
            sysinfo = f"""
System time: {vandaag}
Bot version: {version}
Uptime     : {self.secondsToText(seconds)}
Users      : {sys_info['data']['num_users']}
Eerste  💡 : {sys_info['data']['first_gas_date']} {self.dutch_floats(sys_info['data']['first_gas_price'])}
Eerste  🔥 : {sys_info['data']['first_electra_date']} {self.dutch_floats(sys_info['data']['first_electra_price'])}
CPU load   : {self.get_cpu_usage_pct()}%
RAM usage  : {int(self.get_ram_usage() / 1024 / 1024)} MB
"""
            sysinfo = escape_markdown(sysinfo, version=2)
            msg_sysinfo = f"""

Systeem informatie:
```
{sysinfo}
```"""
            msg_end = escape_markdown( """Dit systeem is gebouwd onder MIT license. Meer informatie op """, version=2)
            msg_github_url = """[Energieprijzenbot\.NL](http://energieprijzenbot\.nl/)"""

            return msg_sysinfo + msg_end + msg_github_url

        except Exception as e:
            log.error(e, exc_info=True)
            return "Oeps er ging iets fout"

    def fileSize(self, filePath):
        try:
            size = os.path.getsize(filePath)
            return self.unitConvertor(size)
        except Exception as e:
            log.error(e, exc_info=True)

    # some other functions
    @staticmethod
    def unitConvertor(sizeInBytes):
        try:
            #Cinverts the file unit
            if sizeInBytes < 1024*1024:
                size = round(sizeInBytes/1024)
                return f"{size} KB"
            elif sizeInBytes < 1024*1024*1024:
                size = round(sizeInBytes/(1024*1024))
                return f"{size} MB"
            elif sizeInBytes >= 1024*1024*1024:
                size = round(sizeInBytes/(1024*1024*1024))
                return f"{size} GB"
            else:
                return f"{sizeInBytes} Bytes"
        except Exception as e:
            log.error(e, exc_info=True)


    @staticmethod
    def get_ram_usage():
        return int(psutil.virtual_memory().total - psutil.virtual_memory().available)

    @staticmethod
    def get_cpu_usage_pct():
        return psutil.cpu_percent(interval=0.5)

    @staticmethod
    def secondsToText(unit, granularity = 2):
        try:
            ratios = {
                'decennia' : 311040000, # 60 * 60 * 24 * 30 * 12 * 10
                'jaar'   : 31104000,  # 60 * 60 * 24 * 30 * 12
                'maanden'  : 2592000,   # 60 * 60 * 24 * 30
                'dagen'    : 86400,     # 60 * 60 * 24
                'uur'   : 3600,      # 60 * 60
                'minuten' : 60,        # 60
                'seconden' : 1          # 1
            }

            texts = []
            for ratio in ratios:
                result, unit = divmod(unit, ratios[ratio])
                if result:
                    if result == 1:
                        ratio = ratio.rstrip('s')
                    texts.append(f'{result} {ratio}')
            texts = texts[:granularity]
            if not texts:
                return f'0 {list(ratios)[-1]}'
            text = ', '.join(texts)
            if len(texts) > 1:
                index = text.rfind(',')
                text = f'{text[:index]},{text[index + 1:]}'
            return text
        except Exception as e:
            log.error(e, exc_info=True)