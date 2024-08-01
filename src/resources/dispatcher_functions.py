import os,sys
from datetime import datetime, timedelta
from time import time
import telegram
from telegram import ParseMode, LabeledPrice
from telegram.utils.helpers import escape_markdown

import logging

from models.api_requests import API_Requests
from resources.help import Help
from resources.onderhoud import Onderhoud
from resources.prices import Prices
from resources.stuur_bericht import StuurBericht
from resources.system import System
from resources.user import Users

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class UnKnownException(Exception):
    pass

class Dispatcher_Functions(object):
    def __init__(self, *args, **kwargs) -> None:
        try:
            self.config = kwargs['config']

            # admin_ids = self.config['admin']['ids'].split(',')
            self.admin_ids = [int(x) for x in self.config['admin']['ids'].split(',')]
            self.telegram_key = self.config['telegram']['key']

            #API Credentials
            self.api_credentials = {}

            self.api_credentials['ip'] = self.config['API']['ip']
            self.api_credentials['port'] = self.config['API']['port']
            self.api_credentials['http'] = self.config['API']['http']
            self.api_credentials['email'] = self.config['login']['email']
            self.api_credentials['password'] = self.config['login']['password']
            self.api_credentials['salt'] =  self.config['login']['salt']
            self.api_credentials['bearer_key'] = ""

            try:
                self.stripe = self.config['stripe']['key']
                self.price = self.config['stripe']['price']
                self.btw = self.config['stripe']['btw']
                self.tokens = self.config['stripe']['tokens']
                self.Custom_Payload = "EP_Bot_APi_TOKENS"
            except KeyError as e:
                log.error(e, exc_info=True)

            dir_path = os.path.dirname(os.path.realpath(__file__))
            self.version_path = os.path.join(dir_path, '..', "VERSION.TXT")
            self.startTime = int(time())

            self.kweetniet = "Sorry dit commando begrijp ik niet."
            self.countries = {}
            self.prijs_instellingen = ['k', 'o', 'a'] #Kaal, Opslag+, Allin

            self.date_hours = []
            super().__init__()
        except KeyError as e:
            log.error(e, exc_info=True)
        except Exception as e:
            log.critical(e, exc_info=True)

    def auto_bot(self, context: telegram.ext.CallbackContext)->None:
        #deze functie handelt automatische meldingen af en haalt de energie prijzen op
        try:
            now = datetime.now()
            cur_hour = int(now.strftime("%H"))

            #If it returns False, it alrady ran this hour
            if not self.check_run_now():
                return
            self.api_credentials['bearer_key'] = API_Requests(api_credentials=self.api_credentials).get_bearer_key()
            self.countries = {}

            if not self.api_credentials['bearer_key'] or self.api_credentials['bearer_key'] == "":
                raise Exception('No Bearer key!')

            self.ochtend_melding(context=context, hour=cur_hour)
            self.middag_melding(context=context, hour=cur_hour)
            self.onder_bedrag_melding(context=context)

        except Exception as e:
            log.error(e, exc_info=True)

    def start_me_up(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        try:
            if(chat_id := self.get_telegram_user_id(update=update)):
                msg = Help().start_text(update=update)
                context.bot.send_message(chat_id=chat_id, text=msg)
        except Exception as e:
            log.error(e, exc_info=True)

    def login(self, update: telegram.Update, context: telegram.ext.CallbackContext)->None:
        try:
            if(chat_id := self.get_telegram_user_id(update=update)):
                try:
                    if context.args[0] == 'help':
                        msg = Help().login()
                    else:
                        raise IndexError
                except IndexError:
                    pass
                login_secret = self.config['login']['secret']
                if (user := Users(api_credentials=self.api_credentials).get_user_by_id(user_id=chat_id)):
                    hash = API_Requests.login_hash(user_id=chat_id, user_salt=user['data'][0]['salt_key'] ,login_secret=login_secret)
                    msg = f"https://users.energieprijzenbot.nl/?login={hash}"
                    context.bot.send_message(chat_id=chat_id, text=msg)
                else:
                    msg = "U bestaat niet in het het systeem!"
        except Exception as e:
            log.error(e, exc_info=True)


    def ochtend_melding(self, context: telegram.ext.CallbackContext, hour:int=8)->None:
        try:
            if (users := Users(api_credentials=self.api_credentials).get_ochtend_users(hour=hour)):
                for user in users['data']:
                    try:
                        id = user['user_id']
                        if (msg := Prices(api_credentials=self.api_credentials).ochtend_prices(user=user)):
                            msg = msg + " Meer prijzen zien? /vandaag"
                            try:
                                context.bot.send_message(chat_id=id, text=msg, disable_web_page_preview=True)
                            except Exception as e:
                                log.error(f"ID not found? {id}, {e}")
                                pass
                    except KeyError as e:
                        log.error(e, exc_info=True)
                        pass
        except Exception as e:
            log.error(e, exc_info=True)

    def middag_melding(self, context: telegram.ext.CallbackContext, hour:int=15)->None:
        try:
            #get morgen message
            if (users := Users(api_credentials=self.api_credentials).get_middag_users(hour=hour)):
                if len(users['data']) > 0:
                    for user in users['data']:
                        id = user['user_id']
                        if(msg:=Prices(api_credentials=self.api_credentials).date_prices(user_id=user['user_id'], prijs_instelling=None)):
                            try:
                                context.bot.send_message(chat_id=id, text=msg, disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN_V2)
                            except Exception as e:
                                log.error(f"ID not found? {id}, {e}")
                                pass
        except Exception as e:
            log.error(e, exc_info=True)

    def onder_bedrag_melding(self, context: telegram.ext.CallbackContext)->None:
        try:
            next_hour_ts = datetime.now()+ timedelta(hours=+1)
            next_hour = next_hour_ts.strftime("%H:00")
            now = datetime.now()
            date = now.strftime("%Y-%m-%d")

            prices = None
            if(next_prices := Prices(api_credentials=self.api_credentials).get_next_hour_price(datum=date, next_hour=next_hour, kind="e")):
                prices = []
                try:
                    for price in next_prices['data']:
                        prices.append({"kind": "k", "price": price['price']})
                        prices.append({"kind": "o", "price": price['opslag_price']})
                        prices.append({"kind": "a", "price": price['all_in_price']})
                except (KeyError, TypeError) as e:
                    log.error(e, exc_info=True)

            users = Users(api_credentials=self.api_credentials).get_users()

            if prices is not None:
                for price in prices:
                    soort = API_Requests.prijs_instelling_tekst(instelling=price['kind'])
                    ids = []

                    try:
                        if users['data'] is None or users['data'][0] is None:
                            raise Exception
                    except (Exception, KeyError):
                        # Geen user data blijkbaar (bij lege db) dus terug naar af!
                        return

                    for user in users['data']:
                        try:
                            if user['kaal_opslag_allin'] == price['kind'] and user['melding_lager_dan'] >= price['price']:
                                ids.append(user['user_id'])
                        except (Exception, KeyError):
                            pass
                    if ids:
                        prijs = API_Requests.dutch_floats(price['price'], my_locale=user['locale'])
                        msg = f"Om {next_hour} gaat de {soort}💡 prijs naar {prijs}"
                        msg = escape_markdown(msg, version=2)
                        # StuurBericht(config=self.config, api_credentials=self.api_credentials)._bepaalde_gebruikers_md(context=context, msg=msg, ids=ids)
                        StuurBericht(api_credentials=self.api_credentials)._bepaalde_gebruikers_md(context=context, msg=msg, ids=ids)
        except Exception as e:
            log.error(e, exc_info=True)

    def bericht(self, update: telegram.Update, context: telegram.ext.CallbackContext)->None:
        try:
            if(chat_id := self.get_telegram_user_id(update=update)):
                if int(chat_id) not in self.admin_ids:
                    msg = "Sorry ik weet niet wat u bedoelt"
                    context.bot.send_message(chat_id=chat_id, text=msg)
                    return

                try:
                    msg  = ' '.join(context.args)
                except IndexError:
                    return False
                except Exception:
                    return False

                if msg is not None and msg != "":
                    # StuurBericht(config=self.config, api_credentials=self.api_credentials)._alle_gebuikers(context=context,msg=msg)
                    StuurBericht( api_credentials=self.api_credentials)._alle_gebuikers(context=context,msg=msg)

        except Exception as e:
            log.error(e, exc_info=True)

    @staticmethod
    def dagen_toekomst(dagen:int = 30)->str:
        try:
            vandaag_ts = datetime.now()
            dagen = f"+{dagen}"
            toekomst_tf = vandaag_ts + timedelta(days=dagen)
            return toekomst_tf.strftime("%Y-%m-%d")
        except Exception as e:
            log.error(e, exc_info=True)

    def upgrade_tokens(self, update: telegram.Update, context: telegram.ext.CallbackContext)->None:
        try:
            if(chat_id := self.get_telegram_user_id(update=update)):
                if int(chat_id) not in self.admin_ids:
                    raise UnKnownException(self.kweetniet)

                try:
                    user_id = int(context.args[0])
                    tokens = int(context.args[1])
                except IndexError:
                    pass
                msg = "Je moet wel een User id en tokens meesturen!"
                if user_id > 0 and tokens > 0 :
                    dagen_toekomst = self.dagen_toekomst()
                    if Users(api_credentials=self.api_credentials)._set_user_tokens(user_id=user_id, tokens=tokens, api_date=dagen_toekomst):
                        msg = "User met tokens geupdate!"
                    else:
                        msg = "User niet geupdate.. error error!!"

                context.bot.send_message(chat_id=chat_id, text=msg)

        except UnKnownException as msg:
            context.bot.send_message(chat_id=chat_id, text=msg)
        except Exception as e:
            log.error(e, exc_info=True)


    def onderhoud(self, update: telegram.Update, context: telegram.ext.CallbackContext)->None:
        try:
            if(chat_id := self.get_telegram_user_id(update=update)):
                if int(chat_id) not in self.admin_ids:
                    raise UnKnownException(self.kweetniet)

                if (msg := Onderhoud().start(context=context)):
                    # StuurBericht(config=self.config, api_credentials=self.api_credentials)._alle_gebuikers(context=context,msg=msg)
                    StuurBericht(api_credentials=self.api_credentials)._alle_gebuikers(context=context,msg=msg)
                else:
                    raise UnKnownException(Onderhoud()._kweetnie)

        except UnKnownException as msg:
            context.bot.send_message(chat_id=chat_id, text=msg)
        except Exception as e:
            log.error(e, exc_info=True)

    def show_current(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            if(chat_id := self.get_telegram_user_id(update=update)):
                prijs_instelling = None
                try:
                    if (context.args[0] in ['k', 'o', 'a']):
                        prijs_instelling = context.args[0]
                except IndexError:
                    pass

                if not (msg := Prices(api_credentials=self.api_credentials).get_cur_price(prijs_instelling=prijs_instelling, user_id=chat_id)):
                    msg = "Sorry er ging iets fout"
                context.bot.send_message(chat_id=chat_id, text=escape_markdown(msg, version=2), parse_mode=ParseMode.MARKDOWN_V2)
        except Exception as e:
            log.error(e, exc_info=True)

    def show_today(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            if(chat_id := self.get_telegram_user_id(update=update)):
                prijs_instelling = None
                try:
                    if (context.args[0] in ['k', 'o', 'a']):
                        prijs_instelling = context.args[0]
                except IndexError:
                    pass

                if not (msg := Prices(api_credentials=self.api_credentials).vandaag_prices(prijs_instelling=prijs_instelling, user_id=chat_id)):
                    msg = "Sorry er ging iets fout"
                context.bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.MARKDOWN_V2)
        except Exception as e:
            log.error(e, exc_info=True)

    def show_tomorrow(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            if(chat_id := self.get_telegram_user_id(update=update)):
                prijs_instelling = None
                try:
                    if (context.args[0] in ['k', 'o', 'a']):
                        prijs_instelling = context.args[0]
                except IndexError:
                    pass

                if not (msg := Prices(api_credentials=self.api_credentials).date_prices(prijs_instelling=prijs_instelling, user_id=chat_id)):
                    msg = "Er zijn op dit moment nog geen prijzen voor morgen"
                context.bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.MARKDOWN_V2)
        except Exception as e:
            log.error(e, exc_info=True)

    def set_locale(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            if(chat_id := self.get_telegram_user_id(update=update)):
                my_locale = None
                try:
                    if context.args[0] == 'help':
                        my_locale = None
                    else:
                        if (context.args[0] in ['en_US', 'nl_NL', 'en_GB', 'de_DE']):
                            my_locale = context.args[0]

                except (KeyError, Exception):
                    pass

                if my_locale is None:
                    msg = Help().locale_help()
                    context.bot.send_message(chat_id=chat_id, text=msg)
                    return

                if not(msg := Users(api_credentials=self.api_credentials).set_locale(context=context, user_id=chat_id)):
                    msg = "Sorry er ging iets mis"

                context.bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.MARKDOWN_V2)
        except Exception as e:
            log.error(e, exc_info=True)

    def show_past(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            if(chat_id := self.get_telegram_user_id(update=update)):

                prijs_instelling = None
                past_date = None
                format_yyyymmdd = "%Y-%m-%d"
                msg = None
                try:
                    if context.args[0] == 'help':
                        msg = Help().verleden_help()
                    else:
                        if (context.args[0] in ['k', 'o', 'a']):
                            prijs_instelling = context.args[0]

                        try:
                            datetime.strptime(context.args[1], format_yyyymmdd).date()
                            past_date = context.args[1]
                        except (ValueError,IndexError):
                            past_date = None
                            pass

                        if past_date is None:
                            try:
                                datetime.strptime(context.args[0], format_yyyymmdd).date()
                                past_date = context.args[0]
                            except (ValueError,IndexError):
                                past_date is None
                                pass

                        if past_date is None:
                            msg = "Geen juiste datum gevonden. \nVoorbeeld datum : 2022-05-14 \n[YYYY-MM-DD]"

                except IndexError:
                    msg = "Oeps, er ging iets fout!"
                    pass

                if msg is not None:
                    context.bot.send_message(chat_id=chat_id, text=msg)
                    # , parse_mode=ParseMode.MARKDOWN_V2
                    return True

                if not (msg := Prices(api_credentials=self.api_credentials).date_prices(prijs_instelling=prijs_instelling, get_date=past_date, user_id=chat_id)):
                    msg = f"Sorry, we hebben geen energie prijzen gevonden voor {past_date}"

                context.bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.MARKDOWN_V2)
        except Exception as e:
            log.error(e, exc_info=True)

    def help(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        try:
            if(chat_id := self.get_telegram_user_id(update=update)):
                msg = Help().help_text(update=update)

                context.bot.send_message(chat_id=chat_id,
                                        text=msg, parse_mode=ParseMode.MARKDOWN_V2,
                                        disable_web_page_preview=True)
        except Exception as e:
            log.error(e, exc_info=True)

    def donate(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            if(chat_id := self.get_telegram_user_id(update=update)):

                try:
                    if context.args[0] == 'help':
                        msg = Help().donatie_help()
                    else:
                        raise IndexError
                except IndexError:
                    msg = "https://donatie.energieprijzenbot.nl"

                context.bot.send_message(chat_id=chat_id, text=msg,
                                        disable_web_page_preview=True)
        except Exception as e:
            log.error(e, exc_info=True)

    def systeminfo(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            if(chat_id := self.get_telegram_user_id(update=update)):

                msg = None
                try:
                    if context.args[0] == 'help':
                        msg = escape_markdown(Help.systeem_help(), version=2)
                except IndexError:
                    pass

                if msg is None or msg == "":
                    versie_path = self.version_path
                    version = open(versie_path, "r").read().replace('\n','')
                    seconds = int(time()) - int(self.startTime)
                    msg = System(api_credentials=self.api_credentials).systeminfo_msg(version=version, seconds=seconds)

                context.bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.MARKDOWN_V2,
                                        disable_web_page_preview=True )

        except Exception as e:
            log.error(e, exc_info=True)

    def aanmelden(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        try:
            if(chat_id := self.get_telegram_user_id(update=update)):

                try:
                    if context.args[0] == 'help':
                        msg = Help().aanmelden_help()
                    else:
                        raise IndexError
                except IndexError:
                    pass

                if Users(api_credentials=self.api_credentials).get_user_by_id(user_id=chat_id):
                    msg = "U staat al in het systeem!"
                else:
                    msg = Users(api_credentials=self.api_credentials).save_user(user_id=chat_id, msg=True)

                if msg is None or msg == "":
                    msg = "Oeps er ging iets fout!"

                context.bot.send_message(chat_id=chat_id, text=msg)
        except KeyError as e:
            log.error(e, exc_info=True)
        except Exception as e:
            log.error(e, exc_info=True)

    def verwijderme(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        try:
            if(chat_id := self.get_telegram_user_id(update=update)):
                msg = None
                try:
                    if context.args[0] == 'help':
                        msg = Help().afmelden_help()
                except IndexError:
                    pass

                if msg is None or msg == "":
                    if Users(api_credentials=self.api_credentials).get_user_by_id(user_id=chat_id):
                        msg = Users(api_credentials=self.api_credentials).del_user(user_id=chat_id, msg=True)
                    else:
                        msg = "U staat niet in het systeem!"

                context.bot.send_message(chat_id=chat_id, text=msg)
        except KeyError as e:
            log.error(e, exc_info=True)
        except Exception as e:
            log.error(e, exc_info=True)

    def instellingen(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        try:
            if(chat_id := self.get_telegram_user_id(update=update)):

                msg = None
                try:
                    if context.args[0] == 'help':
                        msg = escape_markdown(Help.get_instellingen_help(), version=2)
                except IndexError:
                    pass

                if msg is None or msg == "":
                    if not (msg := Users(api_credentials=self.api_credentials).get_instellingen(user_id=chat_id)):
                        msg = "Heeft u zich al aangemeld\? Om aan te melden /aanmelden "

                context.bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.MARKDOWN_V2,
                                        disable_web_page_preview=True )
        except Exception as e:
            log.error(e, exc_info=True)

    def user_api_data(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        try:
            if(chat_id := self.get_telegram_user_id(update=update)):
                msg = None
                try:
                    if context.args[0] == 'help':
                        msg = Help().api_help()
                except IndexError:
                    pass

                if msg is None or msg == "":
                    if not (msg := Users(api_credentials=self.api_credentials).get_api_data(user_id=chat_id)):
                        msg = "Heeft u zich al aangemeld\? Om aan te melden /aanmelden "

                context.bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.MARKDOWN_V2,
                                        disable_web_page_preview=True)
        except Exception as e:
            log.error(e, exc_info=True)

    def opwaarderen(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        try:
            if(chat_id := self.get_telegram_user_id(update=update)):
                msg = None
                arg = None
                try:
                    arg = context.args[0]
                except IndexError:
                    pass


                if arg is not None and arg == 'help':
                    msg = Help().opwaarderen_help()
                    context.bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.MARKDOWN_V2,
                                                disable_web_page_preview=True)
                else:
                    out = context.bot.send_invoice(
                                                    chat_id=chat_id,
                                                    title="Opwaarderen Energieprijzenbot API",
                                                    description= f"Voor {self.tokens} API-Calls",
                                                    start_parameter= 'get_access',
                                                    provider_token=self.stripe,
                                                    payload=self.Custom_Payload,
                                                    currency="EUR",
                                                    prices=[LabeledPrice(f"{self.tokens} API Tokens", self.price), LabeledPrice(f"BTW", self.btw)],
                                                    need_name=True,
                                                    need_email=True)
        except Exception as e:
            log.error(e, exc_info=True)

    def pre_checkout_handler(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        try:
            """https://core.telegram.org/bots/api#answerprecheckoutquery"""
            query = update.pre_checkout_query
            # check the payload, is this from your bot?
            if query.invoice_payload != self.Custom_Payload:
            # answer False pre_checkout_query
                query.answer(ok=False, error_message="Something went wrong...")
            else:
                query.answer(ok=True)

        except Exception as e:
            log.error(e, exc_info=True)

    def successful_payment_callback(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        try:
            receipt = update.message.successful_payment
            print(receipt)
            if(chat_id := self.get_telegram_user_id(update=update)):
                # TODO hier moet ik dus de tokens opwaarderen
                # {'new_chat_members': [], 'delete_chat_photo': False, 'reply_markup':
                # {'inline_keyboard': [[{'pay': True, 'text': 'Pay 2,99\xa0€'}]]},
                # 'chat': {'type': 'private', 'last_name': 'Van der Sluijs', 'id': 1348381054, 'username': 'tvdsluijs', 'first_name': 'Theo'},
                # 'date': 1669028670, 'photo': [], 'entities': [], 'channel_chat_created': False, 'group_chat_created': False,
                # 'supergroup_chat_created': False, 'caption_entities': [], 'new_chat_photo': [], 'message_id': 3990, 'invoice':
                # {'total_amount': 299, 'description': 'Voor 750 API-Calls', 'currency': 'EUR', 'title': 'Opwaarderen Energieprijzenbot AP',
                # 'start_parameter': ''}, 'from': {'first_name': 'Test energie prijzenpot', 'id': 5333121927, 'is_bot': True, 'username':
                # 'Testenergieprijzenbot'}}

                # {'provider_payment_charge_id': 'ch_3M6XsiASogZMgRCF0Pg9Vepf', 'invoice_payload': 'EP_Bot_APi_TOKENS',
                # 'order_info': {'email': 'theo@vandersluijs.nl', 'name': 'Theo'}, '
                # telegram_payment_charge_id': '5333121927_1348381054_6819_7168424764634046464', 'currency': 'EUR', 'total_amount': 299}

                update.message.reply_text("Bedankt voor je aankoop!")
        except Exception as e:
            log.error(e, exc_info=True)


    def api_key(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        try:
            if(chat_id := self.get_telegram_user_id(update=update)):
                msg = None
                try:
                    if context.args[0] == 'help':
                        msg = Help().api_key_help()
                except IndexError:
                    pass

                if msg is None or msg == "":
                    if not (msg := Users(api_credentials=self.api_credentials).get_new_api_key(user_id=chat_id)):
                        msg = "Heeft u zich al aangemeld\? Om aan te melden /aanmelden "

                context.bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.MARKDOWN_V2,
                                        disable_web_page_preview=True)
        except Exception as e:
            log.error(e, exc_info=True)

    def opslag_instellen(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        try:
            if(chat_id := self.get_telegram_user_id(update=update)):

                msg = None
                try:
                    if context.args[0] == 'help':
                        msg = Help().opslag_instellen_help()
                except IndexError:
                    pass

                if msg is None or msg == "":
                    msg = Users(api_credentials=self.api_credentials).set_opslag(context=context, user_id=chat_id)

                context.bot.send_message(chat_id=chat_id, text=msg)
        except Exception as e:
            log.error(e, exc_info=True)

    def ode_instellen(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        try:
            if(chat_id := self.get_telegram_user_id(update=update)):

                msg = None
                try:
                    if context.args[0] == 'help':
                        msg = Help().ode_instellen_help()
                except IndexError:
                    pass

                if msg is None or msg == "":
                    msg = Users(api_credentials=self.api_credentials).set_ode(context=context, user_id=chat_id)

                context.bot.send_message(chat_id=chat_id, text=msg)
        except Exception as e:
            log.error(e, exc_info=True)

    def eb_instellen(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        try:
            if(chat_id := self.get_telegram_user_id(update=update)):

                msg = None
                try:
                    if context.args[0] == 'help':
                        msg = Help().eb_instellen_help()
                except IndexError:
                    pass

                if msg is None or msg == "":
                    msg = Users(api_credentials=self.api_credentials).set_eb(context=context, user_id=chat_id)

                context.bot.send_message(chat_id=chat_id, text=msg)
        except Exception as e:
            log.error(e, exc_info=True)

    def ochtend_instellen(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        try:
            if(chat_id := self.get_telegram_user_id(update=update)):
                msg = None
                try:
                    if context.args[0] == 'help':
                        msg = Help().ochtend_instellen_help()
                except IndexError:
                    pass

                if msg is None or msg == "":
                    msg = Users(api_credentials=self.api_credentials).set_ochtend(context=context, user_id=chat_id)

                context.bot.send_message(chat_id=chat_id, text=msg)
        except Exception as e:
            log.error(e, exc_info=True)

    def soort_prijs_instellen(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        try:
            if(chat_id := self.get_telegram_user_id(update=update)):
                msg = None
                try:
                    if context.args[0] == 'help':
                        msg = Help().soort_prijs_instellen_help()
                except IndexError:
                    pass

                if msg is None or msg == "":
                    msg = Users(api_credentials=self.api_credentials).set_soortprijs(context=context, user_id=chat_id)

                context.bot.send_message(chat_id=chat_id, text=msg)
        except Exception as e:
            log.error(e, exc_info=True)

    def ld_instellen(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        """Lager Dan prijs instellen"""
        try:
            if(chat_id := self.get_telegram_user_id(update=update)):
                msg = None
                try:
                    if context.args[0] == 'help':
                        msg = Help().ld_instellen_help()
                except IndexError:
                    pass

                if msg is None or msg == "":
                    msg = Users(api_credentials=self.api_credentials).set_lagerdan(context=context, user_id=chat_id)

                context.bot.send_message(chat_id=chat_id, text=msg)
        except Exception as e:
            log.error(e, exc_info=True)

    def middag_instellen(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        try:
            if(chat_id := self.get_telegram_user_id(update=update)):
                msg = None
                try:
                    if context.args[0] == 'help':
                        msg = Help().middag_instellen_help()
                except IndexError:
                    pass

                if msg is None or msg == "":
                    msg = Users(api_credentials=self.api_credentials).set_middag(context=context, user_id=chat_id)

                context.bot.send_message(chat_id=chat_id, text=msg)
        except Exception as e:
            log.error(e, exc_info=True)


    def check_run_now(self)->bool:
        try:
            now = datetime.now()
            date_hour = now.strftime("%Y-%m-%d %H:00")

            # Check if current hour in , if so do not run!
            if date_hour in self.date_hours:
                return False #don't run!

            # hour not in list so do somehtings
            self.date_hours.append(date_hour) # add hour to list
            self.date_hours = self.date_hours[-5:] # remove last hour
            return True # RUN RUN RUN
        except Exception as e:
            log.error(e, exc_info=True)

    @staticmethod
    def get_telegram_user_id(update: telegram.Update)->int:
        try:
            return update.message.chat.id #deze is met punt
        except (AttributeError, Exception):
             pass

        try:
            return update.message.chat_id #deze lis met liggend streepje
        except (AttributeError, Exception):
             pass

        return False #niks dan false
