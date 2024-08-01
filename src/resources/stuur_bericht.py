import os
import logging
import telegram

from resources.user import Users
from telegram import ParseMode

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class StuurBericht:
    # def __init__(self, config:dict = None, api_credentials:dict = None) -> None:
    def __init__(self, api_credentials:dict = None) -> None:
        # self.config = config
        self.api_credentials = api_credentials
        pass

    def _alle_gebuikers(self, context: telegram.ext.CallbackContext, msg:str = None)->bool:
        try:
            if msg is None:
                return False
            ids = Users(api_credentials=self.api_credentials).get_user_ids()

            return self._bepaalde_gebuikers(context=context, msg=msg, ids=ids)
        except Exception as e:
            log.error(e, exc_info=True)
            return False

    def _bepaalde_gebuikers(self, context: telegram.ext.CallbackContext, msg:str = None, ids:list = None)->bool:
        try:
            if msg is None or ids is None:
                return False

            for id in ids:
                if id == 0:
                    continue
                try:
                    context.bot.send_message(chat_id=id, text=msg,
                                             disable_web_page_preview=True)
                except Exception as e:
                    log.error(e, id)
                    pass

            return True
        except Exception as e:
            log.error(e, exc_info=True)
            return False

    def _bepaalde_gebruikers_md(self, context: telegram.ext.CallbackContext, msg:str = None, ids:list = None)->bool:
        try:
            if msg is None or ids is None:
                return False

            for id in ids:
                if id == 0:
                    continue
                try:
                    context.bot.send_message(chat_id=id, text=msg, parse_mode=ParseMode.MARKDOWN_V2)
                except Exception as e:
                    log.error(e, id)
                    pass
            return True
        except Exception as e:
            log.error(e, exc_info=True)
            return False
