import os
import logging

import telegram
from telegram.utils.helpers import escape_markdown

from models.users import API_users

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class Users(API_users):
    def __init__(self,*args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def save_user(self, user_id:int = None, msg:bool = False)->bool:
        try:
            if user_id is None:
                return False
            data = self._add_user(user_id=user_id)
            if data and data['msg'] == 'succes':
                if msg:
                    return """U bent toegevoegd aan het systeem!

U krijgt rond 8 uur en rond 16 uur een automatisch inkoopprijzen bericht. U krijg ook bericht wanneer de inkoopprijzen onder de 0.001 zakt.

Via /instellingen kunt u uw instellingen aanpassen"""
                else:
                    return True
        except Exception as e:
            log.error(e, exc_info=True)
            if msg:
                return "Er is iets fout gegaan bij het opslaan van de gebruiker"
            else:
                return False

    def update_user_tokens(self, user_id:int, tokens:int)->bool:
        try:
            if user_id is None:
                return False

            return self._set_middag_user

            return self._get_user_by_id(user_id=user_id)
        except Exception as e:
            log.error(e, exc_info=True)
            return False

    def get_user_by_id(self, user_id:int)->dict:
        try:
            if user_id is None:
                return {}
            return self._get_user_by_id(user_id=user_id)
        except Exception as e:
            log.error(e, exc_info=True)
            return {}

    def get_user_ids(self)->list:
        try:
            return self._get_user_ids()
        except Exception as e:
            log.error(e, exc_info=True)
            return ()

    def get_users(self)->list:
        try:
            return self._get_users()
        except Exception as e:
            log.error(e, exc_info=True)
            return ()

    def del_user(self, user_id:int = None, msg:bool = False)->str:
        try:
            if user_id is None:
                return False
            data = self._remove_user(user_id=user_id)
            if data:
                if msg:
                    return """U bent verwijderd uit het systeem!
Uw API Sleutel is verwijderd.

U ontvangt geen berichten meer.
U kunt nog wel gebruik maken van deze Bot.
"""
                else:
                    return True
        except Exception as e:
            log.error(e, exc_info=True)
            if msg:
                return "Er is iets fout gegaan bij het verwijderen"
            else:
                return False

    def get_ochtend_users(self, hour:int=8)->list:
        try:
            return self._get_ochtend_users(hour=hour)
        except Exception as e:
            log.error(e, exc_info=True)
            return False

    def get_middag_users(self, hour:int=15)->dict:
        try:
            return self._get_middag_users(hour=hour)
        except Exception as e:
            log.error(e, exc_info=True)
            return ()

    def get_new_api_key(self, user_id:int)->str:
        try:
            if not (data := self.get_user_by_id(user_id=user_id)):
                # niks gevonden blijkbaar
                return "U staat niet in het systeem\! Om u aan te melden /aanmelden"

            data = {"new_api_key":True}
            if(data := self._set_user_value(user_id=user_id, data=data)):
                api_key = data['data']['api_key']
                msg = f"""
Je nieuwe API sleutel is

{api_key}

Lees: [Hoe gebruik je de API](https://eprijzen.nl/project_category/api/)
"""

            return msg

        except Exception as e:
            log.error(e, exc_info=True)
            return False

    def get_api_data(self, user_id:int = None)->str:
        try:
            if not (data := self.get_user_by_id(user_id=user_id)):
                # niks gevonden blijkbaar
                return "U staat niet in het systeem\! Om u aan te melden /aanmelden"

            try:
                user = data['data'][0]
                if user is None:
                    raise Exception
            except Exception:
                return "U staat niet in het systeem\! Om u aan te melden /aanmelden"

            msg = """
API Gegevens

Geef nooit je API Sleutel aan iemand anders\!

Lees: [Hoe gebruik je de API](https://eprijzen.nl/project_category/api/)"""

# API prijs:  {user['api_price']}
            api = escape_markdown(f"""
API coins over:  {user['api_calls']}
""", version=2)

            msg += f"""
```
{api}
```"""

            try:
                msg += escape_markdown(f"""
API Sleutel:

{user['api_key']}
""", version=2)
            except (Exception, KeyError) as e:
                msg +=  escape_markdown(f"""Het lijkt er op dat je nog geen API sleutel hebt.
Genereer een API key via
/apikey
""", version=2)
                msg += """
Je kan met dit commando ook een nieuwe API sleutel maken, voor als je hem per ongeluk toch hebt gedeeld\!"""
                pass

            return msg
        except Exception as e:
            log.error(e, exc_info=True)
            return False

    def get_instellingen(self, user_id:int = None)->str:
        try:
            if not (data := self.get_user_by_id(user_id=user_id)):
                # niks gevonden blijkbaar
                return "U staat niet in het systeem\! Om u aan te melden /aanmelden"

            try:
                user = data['data'][0]
                if user is None:
                    raise Exception
            except Exception:
                return "U staat niet in het systeem\! Om u aan te melden /aanmelden"

            msg = escape_markdown(f"""Uw user id is {user['user_id']}

""", version=2)

            msg += """U ontvangt de volgende berichten:
"""
            update = "nvt"
            try:
                if user['ochtend'] is not None:
                    update = f"{user['ochtend']} uur"
            except KeyError:
                pass

            msg += f"""
```
Ochtend update  : {update}```"""

            update = "nvt"
            try:
                if user['middag'] is not None:
                    update = f"{user['middag']} uur"
            except KeyError:
                pass

            msg += f"""
```
Middag update   : {update}```"""

            update = "nvt"
            try:
                if user['melding_lager_dan'] is not None:
                    update = escape_markdown(str(f"€ {user['melding_lager_dan']}"), version=2)
            except KeyError:
                pass

            msg += f"""
```
Bedrag <= update: {update}```"""

            belasting = escape_markdown(f"""
Opslag    💡: {self.dutch_floats(price=user['opslag_electra'], my_locale=user['locale'])}
Belasting 💡: {self.dutch_floats(price=user['eb_electra'], my_locale=user['locale'])}
ODE       💡: {self.dutch_floats(price=user['ode_electra'], my_locale=user['locale'])}

Opslag    🔥: {self.dutch_floats(price=user['opslag_gas'], my_locale=user['locale'])}
Belasting 🔥: {self.dutch_floats(price=user['eb_gas'], my_locale=user['locale'])}
ODE       🔥: {self.dutch_floats(price=user['ode_gas'], my_locale=user['locale'])}

BTW         :  {user['btw']}%""", version=2)

            msg += f"""

Opslag en Belastingen
```
{belasting}
```"""
            prijs_soort = self.prijs_instelling_tekst(instelling=user['kaal_opslag_allin'])

            msg += f"""
```
Prijs instelling: {prijs_soort}
```"""

            msg += f"""
```
Locale: {user['locale']}
```"""

            api = escape_markdown( f"""

API Gegevens
Sleutel: \t/api
Tokens: \t{user['api_calls']}
Geldig tot: \t{user['api_valid_date']}
""", version=2)
            msg += f"```{api}```"

            msg += """
Hulp nodig?
/i help
"""
            return msg
        except KeyError as e:
            log.error(e, exc_info=True)
            return """
U staat niet in het systeem, of er gaat iets fout\!

Aanmelden voor automatische updates\?
/aanmelden
of
/a"""
        except Exception as e:
            log.error(e, exc_info=True)
            return False

    def set_locale(self, context: telegram.ext.CallbackContext, user_id:int = None)->bool:
        try:
            my_locale = context.args[0]
            data = {"locale":my_locale}
            if(data := self._set_user_value(user_id=user_id, data=data)):
                msg = f"Je locale is gezet op {my_locale}"
                return escape_markdown(msg)

            return escape_markdown("Sorry er ging iets mis met het zetten van je locale")
        except Exception as e:
            log.error(e, exc_info=True)


    def set_opslag(self, context: telegram.ext.CallbackContext, user_id:int = None)->bool:
        try:
            try:
                if context.args[0] not in ['e', 'g']:
                    raise IndexError

                if context.args[1] != 'uit':
                    price = float(context.args[1].replace(',', '.'))
                else:
                    price = None

                if context.args[0] == 'e':
                    opslag_soort = "opslag_electra"
                if context.args[0] == 'g':
                    opslag_soort = "opslag_gas"
            except (IndexError, ValueError):
                return """Ik begrijp je niet
Inkoopvergoeding instellen:
/iv [e/g] [bedrag]

Bijvoorbeeld voor electra:
/iv e 0.01694

en voor gas
/iv g 0.0968

of
/iv [e/g] uit
"""

            data = {opslag_soort:price}
            data = self._set_user_value(user_id=user_id, data=data)

            match context.args[0]:
                case 'e':
                    soort = "Electra"
                case 'g':
                    soort = "Gas"

            if data['data']:
                if price is None:
                    msg = f"""De {soort} inkoopvergoeding is nu de standaard systeem vergoeding prijs.

Kijk of je instellingen goed staan
/i
"""
                else:
                    msg =  f"""De {soort} inkoopvergoeding {price} is ingesteld, vergeet niet om je melding soort in te stellen.
Hulp hierover vind je via
/ms help

Kijk of je instellingen goed staan
/i
"""
                return msg

            return "Er ging iets fout"

        except Exception as e:
            log.error(e, exc_info=True)

    def set_ode(self, context: telegram.ext.CallbackContext, user_id:int = None)->bool:
        try:
            try:
                if context.args[0] not in ['e', 'g']:
                    raise IndexError

                if context.args[1] != 'uit':
                    price = float(context.args[1].replace(',', '.'))
                else:
                    price = None

                if context.args[0] == 'e':
                    ode_soort = "ode_electra"
                if context.args[0] == 'g':
                    ode_soort = "ode_gas"

            except (IndexError, ValueError):
                return """Ik begrijp je niet
ODE instellen:
/ODE [e/g] [bedrag]

Bijvoorbeeld voor electra:
/ode e 0.03691

en voor gas
/ode g 0.10467

Standaard ODE aan zetten?
/ode [e/g] uit
"""

            data = {ode_soort:price}
            data = self._set_user_value(user_id=user_id, data=data)

            match context.args[0]:
                case 'e':
                    soort = "Electra"
                case 'g':
                    soort = "Gas"

            if data['data']:
                if price is None:
                    msg = f"""ODE voor {soort} staat nu op de systeem ODE prijs.

Kijk of je instellingen goed staan
/i
"""
                else:
                    msg = f"""De ODE voor {soort} is ingesteld op {price}."""

                return msg

            return "Er ging iets fout"

        except Exception as e:
            log.error(e, exc_info=True)

    def set_eb(self, context: telegram.ext.CallbackContext, user_id:int = None)->bool:
        try:
            try:
                if context.args[0] not in ['e', 'g']:
                    raise IndexError

                if context.args[1] != 'uit':
                    price = float(context.args[1].replace(',', '.'))
                else:
                    price = None

                if context.args[0] == 'e':
                    eb_soort = "eb_electra"
                if context.args[0] == 'g':
                    eb_soort = "eb_gas"

            except (IndexError, ValueError):
                return """Ik begrijp je niet
Energie Belasting instellen:
/iv [e/g] [bedrag]

Bijvoorbeeld voor electra:
/eb e 0.04452

en voor gas
/eb g 0.4395

Standaard Energiebelasing aanzetten?
/eb [e/g] uit
"""

            data = {eb_soort:price}
            data = self._set_user_value(user_id=user_id, data=data)

            match context.args[0]:
                case 'e':
                    soort = "Electra"
                case 'g':
                    soort = "Gas"

            if data['data']:
                if price is None:
                    msg = f"""De Energie Belasting voor {soort} staat nu op de systeem ODE prijs.

Kijk of je instellingen goed staan
/i
"""
                else:
                    msg = f"""De Energie Belasting voor {soort} is ingesteld op {price}."""

                return msg


            return "Er ging iets fout"

        except Exception as e:
            log.error(e, exc_info=True)

    def set_soortprijs(self, context: telegram.ext.CallbackContext, user_id:int = None)->bool:
        try:
            try:
                if context.args[0] not in ['k', 'o', 'a']:
                    raise IndexError
            except (IndexError, ValueError):
                return """Ik begrijp je niet
Soort prijzen instellen

Kale prijs?
/sp k

Inkoopvergoeding & BTW
/sp o

All in prijs
/sp a
"""

            soort = self.prijs_instelling_tekst(instelling=context.args[0])

            data = {"kaal_opslag_allin":str(context.args[0])}
            data = self._set_user_value(user_id=user_id, data=data)

            if data['data']:
                return f"""Je ontvangt vanaf nu de {soort} prijzen in alle automatische en handmatige meldingen
Wil je even een andere prijs zien bij /nu /vandaag /morgen type er dan een k o of a achter
Bijvoorbeeld:
/vandaag o
"""

            return "Er ging iets fout"

        except Exception as e:
            log.error(e, exc_info=True)

    def set_ochtend(self, context: telegram.ext.CallbackContext, user_id:int = None)->bool:
        aan_uit = None
        try:
            try:
                if context.args[0] == 'uit':
                    aan_uit = 0
                elif int(context.args[0]) in range(0,23):
                    aan_uit = 1
                else:
                    raise IndexError
            except (IndexError, ValueError):
                return """Ik begrijp je niet
Ochtend melding instellen:
/ochtend [uur / 0-23 ]

bijvoorbeeld:
/ochtend 8

of om uit te zetten
/ochtend uit
"""
            if aan_uit == 1:
                data = {"ochtend":int(context.args[0])}
                data = self._set_user_value(user_id=user_id, data=data)
                if data['data']:
                    return f"Je ontvangt vanaf nu ieder dag om ±{int(context.args[0])} uur de ochtend update"
            elif aan_uit == 0:
                data = {"ochtend":None}
                data = self._set_user_value(user_id=user_id, data=data)
                if data['data']:
                    return f"De ochtend melding is uitgezet"

            return "Er ging iets fout"

        except (Exception, KeyError) as e:
            log.error(e, exc_info=True)
            return "Er ging iets fout"

    def set_middag(self, context: telegram.ext.CallbackContext, user_id:int = None)->bool:
        aan_uit = None
        try:
            try:
                if context.args[0] == 'uit' :
                    aan_uit = 0
                elif int(context.args[0]) in range(15,23):
                    aan_uit = 1
                else:
                    raise IndexError
            except (IndexError, ValueError):
                return """Ik begrijp je niet
Middag melding instellen:
/middag [uur / 15-23]

Bijvoorbeeld
/middag 16

of om uit te zetten
/middag uit
"""

            if aan_uit == 1:
                data = {"middag":int(context.args[0])}
                data = self._set_user_value(user_id=user_id, data=data)
                if data['data']:
                    return f"Je ontvangt vanaf nu elke dag om ±{int(context.args[0])} uur de middag prijzen"
            elif aan_uit == 0:
                data = {"middag":None}
                data = self._set_user_value(user_id=user_id, data=data)
                if data['data']:
                    return f"De middag prijzen melding is uitgezet"

            return "Er ging iets fout"

        except (Exception, KeyError) as e:
            log.error(e, exc_info=True)
            return "Er ging iets fout"

    def set_lagerdan(self, context: telegram.ext.CallbackContext, user_id:int = None)->bool:
        aan_uit = None
        try:
            try:
                if context.args[0] == 'uit':
                    aan_uit = 0
                else:
                    price = float(context.args[0].replace(',', '.'))
                    aan_uit = 1
            except IndexError:
                return """Ik begrijp je niet
Wil je iets doen zoals:
/lagerdan -0.10
/lagerdan uit
"""
            if aan_uit == 1:
                data = {"melding_lager_dan":price}
                data = self._set_user_value(user_id=user_id, data=data)
                if data['data']:
                    return f"Je ontvangt nu een melding als de prijs zakt onder de {price}"
            elif aan_uit == 0:
                data = {"melding_lager_dan":None}
                data = self._set_user_value(user_id=user_id, data=data)
                if data['data']:
                    return f"Je automatische lager dan prijs melding staat nu uit."

            return "Er ging iets fout"

        except Exception as e:
            log.error(e, exc_info=True)
