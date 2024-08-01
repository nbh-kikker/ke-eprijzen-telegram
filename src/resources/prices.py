from decimal import Decimal
import os
import logging
from telegram.utils.helpers import escape_markdown

from datetime import datetime, timedelta
from models.prices import API_prices
from resources.user import Users

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

# from functions_sql.prices_sql import PricesSQL

class Prices(API_prices):
    def __init__(self,*args, **kwargs) -> None:

        self.morgen = ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00']
        self.middag = ['12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00']

        super().__init__(*args, **kwargs)

    def get_cur_price(self, prijs_instelling:str = None, datum:str = None, tijd:str = None, user_id:int = None)->str:
        try:
            vandaag_ts = datetime.now()
            user_locale = None
            if datum is None:
                datum = vandaag_ts.strftime("%Y-%m-%d")

            if tijd is None:
                tijd = vandaag_ts.strftime("%H:00")

            if prijs_instelling is None and user_id is not None:
                try:
                    if (data := Users(api_credentials=self.api_credentials).get_user_by_id(user_id=user_id)):
                        user = data['data'][0]
                        prijs_instelling = user['kaal_opslag_allin']
                        user_locale = user['locale']
                except Exception as e:
                    log.error(e, exc_info=True)

            if prijs_instelling is None:
                prijs_instelling = 'k'

            match prijs_instelling:
                case 'k':
                    price_kind = "price"
                case 'o':
                    price_kind = "opslag_price"
                case 'a':
                    price_kind = "all_in_price"
                case _:
                    price_kind = "price"

            data = self._get_prices(datum=datum, tijd=tijd, user_id=user_id)
            if not data:
                return "Sorry, het lijkt er op dat we geen prijzen hebben kunnen ophalen."

            gas = None
            elect = None

            for v in data['data']:
                if v['kind'] == 'e' and v['fromtime'] == tijd:
                    elect = v
                if v['kind'] == 'g' and v['fromtime'] == tijd:
                    gas = v

            try:
                elect_price = self.dutch_floats(elect[price_kind], my_locale=user_locale)
            except (KeyError, TypeError):
                elect_price = ""
            try:
                gas_price = self.dutch_floats(gas[price_kind], my_locale=user_locale)
            except (KeyError, TypeError):
                gas_price = ""

            if elect_price == "" and gas_price == "":
                return "Sorry, het lijkt er op dat we geen prijzen hebben kunnen ophalen vandaag"

            soort = self.prijs_instelling_tekst(instelling=prijs_instelling)

            msg = f"""
{soort}prijzen van {elect['fromtime']} tot {self.next_hour(hour=tijd)}"""

            if elect_price == "":
                msg += """
Sorry geen 💡 prijzen beschikbaar"""
            else:
                msg += f"""
💡 {elect_price}"""
            if gas_price == "":
                msg += """
Sorry geen 🔥 prijzen beschikbaar"""
            else:
                msg += f"""
🔥 {gas_price}"""

            return msg
        except Exception as e:
            log.error(e, exc_info=True)
            return False


#     def get_cur_price_zero_or_lower(self, prijs_instelling:str = 'k')->str:
#         try:
#             vandaag_ts = datetime.now()
#             date = vandaag_ts.strftime("%Y-%m-%d")
#             time = vandaag_ts.strftime("%H:00")

#             data = self._get_prices(date=date)
#             elect = None

#             for v in data:
#                 if v['kind'] == 'e' and v['fromtime'] == time:
#                     elect = v

#             try:
#                 elect_price = self.get_user_correct_pricing(price=elect['price'], kind='e', prijs_instelling=prijs_instelling)
#             except (KeyError, TypeError):
#                 return "Sorry, het lijkt er op dat we geen prijzen hebben kunnen ophalen vandaag"

#             # prijs is hoger dan 0 dus niks nakkes nada en terug
#             if elect_price > 0:
#                 return False

#             prijs = self.dutch_floats(elect_price)
#             soort = self.prijs_instelling_tekst(instelling=prijs_instelling)

#             return f"""
# {soort}prijzen van {elect['fromtime']} tot {self.next_hour(hour=time)}
# 💡 {prijs}"""

#         except Exception as e:
#             log.error(e, exc_info=True)
#             return False


    def ochtend_prices(self, user:dict = None)->str:
        try:
            vandaag_ts = datetime.now()
            vandaag = vandaag_ts.strftime("%Y-%m-%d")
            leesbare_vandaag = self.get_nice_day(date=vandaag, weekday=False)
            price_data = self.get_low_high(date=vandaag, user_id=user['user_id'])

            gas_data = self._get_prices(datum=vandaag, tijd="23:00", kind='g', lowest=True, user_id=user['user_id'])

            elect_low = price_data['elect_low']['data']
            elect_high = price_data['elect_high']['data']
            gas = gas_data['data']

            prijs_instelling = user['kaal_opslag_allin']
            user_locale = user['locale']

            match prijs_instelling:
                case 'k':
                    price_kind = "price"
                case 'o':
                    price_kind = "opslag_price"
                case 'a':
                    price_kind = "all_in_price"
                case _:
                    price_kind = "price"

            try:
                fromtime_low = elect_low[0]['fromtime']
                int_hour_low = int(fromtime_low[:2])
                price = elect_low[0][price_kind]
                gas_price = self.dutch_floats(gas[0][price_kind], my_locale=user_locale)
            except (KeyError, TypeError):
                return "Sorry, het lijkt er op dat we geen prijzen hebben kunnen ophalen vandaag"

            soort_prijs = self.prijs_instelling_tekst(instelling=prijs_instelling)

            low_price = self.dutch_floats(price, my_locale=user_locale)

            i = 0
            for d in elect_low:
                if i == 0:
                    i += 1
                    continue

                next_low = d['fromtime']
                int_next_low = int(next_low[:2])
                if (int_next_low - int_hour_low) == 1:
                    if Decimal(price) == Decimal(d[price_kind]):
                        int_hour_low = int_next_low
                    else:
                         break
                else:
                    break

            fromtime_high = elect_high[0]['fromtime']

            high_price = self.dutch_floats(elect_high[0][price_kind], my_locale=user_locale)

            int_hour_low = int(int_hour_low) + 1
            int_hour_high = int(fromtime_high[:2]) + 1
            totime_low = f"{int_hour_low:02d}:00"
            totime_hight = f"{int_hour_high:02d}:00"

            msg = f"""{soort_prijs}prijs {leesbare_vandaag}
💡kWh laagste {fromtime_low}-{totime_low} {low_price}
💡kWh hoogste {fromtime_high}-{totime_hight} {high_price}
🔥 m³ van 6:00 tot 6:00 {gas_price}

"""

            return msg
        except Exception as e:
            log.error(e, exc_info=True)
            return False

    def get_next_hour_price(self, datum:str=None, next_hour:str=None, kind:str = "e"):
        try:
            return self._get_prices(datum=datum, tijd=next_hour, kind=kind)
            # return {'prijs': prijs, 'msg': msg}
        except Exception as e:
            log.error(e, exc_info=True)
            return False

    def vandaag_prices(self, prijs_instelling:str=None, user_id:int = None)->dict:
        try:
            vandaag_ts = datetime.now()
            vandaag = vandaag_ts.strftime("%Y-%m-%d")
            user_locale = None
            if prijs_instelling is None and user_id is not None:
                try:
                    if (data := Users(api_credentials=self.api_credentials).get_user_by_id(user_id=user_id)):
                        user = data['data'][0]
                        prijs_instelling = user['kaal_opslag_allin']
                        user_locale= user['locale']
                except Exception as e:
                    log.error(e, exc_info=True)

            if prijs_instelling is None:
                prijs_instelling = 'k'

            data = self._get_prices(datum=vandaag, user_id=user_id)
            return self.totaal_overzicht(data=data, date=vandaag, prijs_instelling=prijs_instelling, my_locale=user_locale)

        except Exception as e:
            log.error(e, exc_info=True)
            return False

    def date_prices(self, prijs_instelling:str='k', get_date:str=None, user_id:int = None)->str:
        try:
            if get_date is None:
                morgen_ts = datetime.now() + timedelta(days=+1)
                get_date = morgen_ts.strftime("%Y-%m-%d")

            return self._prices_data(date=get_date, prijs_instelling=prijs_instelling, user_id=user_id)
        except Exception as e:
            log.error(e, exc_info=True)
            return False

    def _prices_data(self, date:str = None, prijs_instelling:str='k', user_id:int = None)->dict:
        try:
            user_locale = None
            if prijs_instelling is None and user_id is not None:
                try:
                    if (data := Users(api_credentials=self.api_credentials).get_user_by_id(user_id=user_id)):
                        try:
                            user = data['data'][0]
                            prijs_instelling = user['kaal_opslag_allin']
                            user_locale = user['locale']
                        except Exception:
                            raise Exception
                except Exception as e:
                    log.error(e, exc_info=True)

            if prijs_instelling is None:
                prijs_instelling = 'k'

            price_data = self._get_prices(datum=date, user_id=user_id)
            if price_data is None:
                return False

            data = price_data['data']
            el_prices = 0
            try:
                for d in data:
                    if d['kind'] == 'e':
                        el_prices = 1
                        break

                # No electric prices, so return
                if el_prices == 0:
                    raise KeyError

            except KeyError as e:
                return False

            return self.totaal_overzicht(data=price_data, date=date, prijs_instelling=prijs_instelling, my_locale=user_locale)
        except Exception as e:
            log.error(e, exc_info=True)
            return False

    def totaal_overzicht(self, data:list=None, date:str=None, prijs_instelling:str = None, my_locale:str=None)->str:
        try:
            soort = self.prijs_instelling_tekst(instelling=prijs_instelling)
            md_soort = escape_markdown(soort, version=2)
            nice_day = escape_markdown(self.get_nice_day(date=date), version=2)
            msg_elect = f"""{nice_day}
{md_soort} prijzen 💡"""
            msg_gas =  f"{md_soort} prijzen 🔥"
            gas_voor = ""
            gas_na = ""
            elec = ""
            msg = ""
            electra = {}

            match prijs_instelling:
                case 'k':
                    price_kind = "price"
                case 'o':
                    price_kind = "opslag_price"
                case 'a':
                    price_kind = "all_in_price"
                case _:
                    price_kind = "price"

            try:
                if data['data'] is None:
                    raise Exception
            except Exception as e:
                return "Er ging iets helemaal mis, probeer het later nog een keer"

            for v in data['data']:
                if v['kind'] == 'e':
                    electra[v['fromtime']] = self.dutch_floats(v[price_kind],my_locale=my_locale)
                if v['kind'] == 'g':
                    tijd = int(v['fromtime'][:-3])
                    if tijd <= 5:
                        gas_voor = f"tot 06:00 {self.dutch_floats(v[price_kind],my_locale=my_locale)}"
                    else:
                        gas_na = f"na 06:00 {self.dutch_floats(v[price_kind], my_locale=my_locale)}"

            for index, item in enumerate(self.morgen):
                elec += f"{self.morgen[index]} {electra[self.morgen[index]]}  {self.middag[index]} {electra[self.middag[index]]}\n"

            msg = f"""{msg_elect}```

{escape_markdown(elec, version=2)}```
{msg_gas}
```
{escape_markdown(gas_voor, version=2)}
{escape_markdown(gas_na, version=2)}```"""

            return msg
        except KeyError as e:
            # Some prices not here, so return
            return False
        except Exception as e:
            log.error(e, exc_info=True)
            return False

    def get_low_high(self, date:str="", user_id:int = None)->dict:
        try:
            if not date:
                vandaag_ts = datetime.now()
                date = vandaag_ts.strftime("%Y-%m-%d")

            elect_low = self._get_prices(datum=date, kind='e', lowest=True, user_id=user_id)
            elect_high = self._get_prices(datum=date, kind='e', highest=True, user_id=user_id)

            return {'elect_low': elect_low, 'elect_high': elect_high}

        except Exception as e:
            log.error(e, exc_info=True)
            return {}

    def all_in_price(self, belasting:dict = None, price:float = None)->float:
        try:
            if price is None:
                return False
            # eerst opslag prijs uitrekenen
            opslag_price = self.opslag_price(belasting=belasting, price=price)

            return opslag_price+float(belasting['ode'])+float(belasting['eb'])

        except KeyError as e:
            log.error(e, exc_info=True)
            return False
        except Exception as e:
            log.error(e, exc_info=True)
            return False
