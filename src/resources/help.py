import os
import logging

import telegram
from telegram.utils.helpers import escape_markdown

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class Help:
    def __init__(self) -> None:
        pass

    def start_text(self, update: telegram.Update)->str:
        name = self.get_name(update=update)

        return f"""
Hoi {name} welkom op deze energie prijzen bot!

Als je je snel wilt aanmelden doe dan
/a

Wil je meer informatie of hulp?

/help
"""
    @staticmethod
    def login()->str:
        return """Hiermee kan je een login url maken naar de user site."""

    def help_text(self, update: telegram.Update)->str:
        name = self.get_name(update=update)
        chat_id = update.message.chat.id
        msg = f"""Hoi {name}, """
        try:
            user_id = update.channel_post.sender_chat.id
            msg +="""

Sorry, op dit moment ondersteunen we nog geen group of channel chats.

We zijn hier wel mee bezig, echter is dit een redelijke aanpassing. Het kan nog even duren voor dit klaar is.
"""
        except Exception:
            msg += """hier is hulp:"""

            msg += f"""
Jouw chat id: {chat_id}

💡 Stroom prijzen
🔥 Gas prijzen

Standaard krijg je de Kale prijzen.
Aanpassen Kaal, Opslag+, All-In?
/sp [k/o/a]
/sp a → all in

Handmatige berichten
/nu → huidige prijzen
/vandaag → Alle prijzen vandaag
/morgen → Alle prijzen morgen*

Zet overal een k, o of a achter voor kale,
opslag+, allin prijzen, bijv:
/morgen o

* prijzen pas na 15u (soms eerder)

Voor automatische berichten:
/a → aanmelden
/i → jouw instellingen
/o 9 → ochtend melding 9 uur
/m 15 → middag melding 15 uur
/ld -0.09 → melding prijs lager dan -0.09

Inkoopvergoeding zetten (ex BTW)
/iv [e/g] [bedrag]
/iv [e/g] uit

ODE en Energiebelasting zetten (ex BTW)
/ode [e/g] [bedrag]
/eb [e/g] [bedrag]
/ode [e/g] uit
/eb [e/g] uit

Gegevens uit het verleden zien?
/verleden [k/o/a] [YYYY-MM-DD]

Wil je een punt ipv een comma in bedragen?
/locale en_GB
wel comma's ipv een punt?
/locale nl_NL

Jouw gegevens verwijderen?
/verwijder

Wil je meer hulp? Zet er help achter
/a help
/i help
enz.
"""
        msg = escape_markdown(msg, version=2)

        msg += """
[Doneren? Ja graag](https://donorbox.org/energieprijzenbot)

Vragen / Bug gevonden? @tvdsluijs
"""
        return msg

    @staticmethod
    def systeem_help()->str:
        return """
Wil je meer informatie over dit systeem?

/s

en je krijg wat info te zien!
"""

    @staticmethod
    def ode_instellen_help()->str:
        return """
Wil je de ODE zelf instellen?
Zet hem via

/ode [e/g] [bedrag]

Bijvoorbeeld voor electra:
/ode e 0.03691

en voor gas
/ode g 0.10467

Je kan de ODE niet uitzetten.

Vergeet daarna niet de melding soort in te stellen
/ms help
"""

    @staticmethod
    def verleden_help()->str:
        return """
Gegevens uit het verleden zien?
/verleden [k/o/a] [YYYY-MM-DD]

/verleden 2022-05-14
Het systeem gebruikt door jou ingestelde gegevens

De kale gegevens zien?
/verleden k 2022-05-14

Met opslag+btw
/verleden o 2022-05-14

All-In prijzen
/verleden a 2022-05-14
"""

    def eb_instellen_help()->str:
        return """
Wil je de Energie Belasting zelf instellen?
Zet hem via

/eb [e/g] [bedrag]

Bijvoorbeeld voor electra:
/eb e 0.04452

en voor gas
/eb g 0.4395

Je kan de Energie Belasting niet uitzetten.

Vergeet daarna niet de melding soort in te stellen
/ms help
"""

    @staticmethod
    def opslag_instellen_help()->str:
        return """
Wil je de inkoopvergoeding (opslag) voor je eigen energieleverancier instellen?

De opslag vergoeding voer je in exclusief BTW.

Zet hem aan via

/iv [e/g] [bedrag]

Bijvoorbeeld voor electra:
/iv e 0.0155412844

en voor gas
/iv g 0.08871559633

wil je de systeem opslag prijzen weer aanhouden?

/iv e uit
/iv g uit

"""

    @staticmethod
    def api_help()->str:
        return """
Je wilt gebruik maken van de API?


"""

    @staticmethod
    def opwaarderen_help()->str:
        # TODO hier moet nog een leuk tekstje komen!
        return """
Hello, dit is een leuk tekstje
"""

    @staticmethod
    def api_key_help()->str:
        return """
Als je nog geen API sleutel hebt of je wilt je API sleutel vernieuwen (omdat je hem toch per ongeluk aan iemand anders hebt gegeven) dan kan je met het commando

/apikey

je API sleutel aanmaken of vernieuwen.

LET OP! Je oude sleutel werkt dan DIRECT niet meer dus pas het aan in Home Assistent of waar je hem nog meer gebruikt.
"""

    @staticmethod
    def soort_prijs_instellen_help()->str:
        return """
Hoe wil je de automatische prijs meldingen zien?

Kale prijs?
/sp k

Inkoopvergoeding & BTW
/sp o

All in prijs
/sp a

Hiermee stel je alle toekomstige meldingen in

Je kan nog steeds de handmatige meldingen doen
"""
    @staticmethod
    def ochtend_instellen_help()->str:
        return """
Wil je een hoog laag melding in de ochtend voor die dag?
Zet hem aan via

/o [uur]

Wil je een melding om 8 uur

/o 8

Een melding om 10 uur
/o 10

Ochtend meldingen uitzetten
/o uit

Je kan maar 1 ochtend melding instellen!
"""

    @staticmethod
    def ld_instellen_help()->str:
        return """
Melding wanneer de prijs lager of gelijk is dan x?

/ld 0,001

of iets als
/ld -0,09

Alle getallen zijn mogelijk.

Let op, als je /sp hebt ingesteld (soort prijs) dan gaat het systeeem uit van jouw instelling, dus kale, opslag of all-in prijzen.

Uitzetten?
/ld uit
"""

    @staticmethod
    def hd_instellen_help()->str:
        return """
Melding wanneer de prijs hoger of gelijk is dan x?

/hd 0,05

of iets als
/ld 0,10

Alle getallen zijn mogelijk, systeem gaat nu nog van inkoop prijs uit.

Uitzetten?
/ld uit"""

    @staticmethod
    def locale_help()->str:
        return """
Wil je een punt ipv een comma in bedragen?
/locale en_GB
→ € 0.342

Wel een comma ipv een punt?
/locale nl_NL
→ € 0,342

Wil je hulp?
/locale help
        """


    @staticmethod
    def middag_instellen_help()->str:
        return """
Wil je automatisch een melding van de prijzen van morgen?
Zet hem aan via

/m [uur]

Wil je een melding om 15 uur

/m 15

Een melding om 17 uur
/m 17

Je kan maar 1 middag melding instellen!
"""

    @staticmethod
    def get_instellingen_help()->str:
        return """
Instellingen hulp
/ochtend [uur]  →  update om 8 uur [1-12]
/ochtend uit → update uit
/middag [uur] → prijzen morgen [16-23]
/middag uit → prijzen morgen uit
/lager [+/- bedrag] → melding prijs lager 0.001
/lager uit → melding lager uit
/iv [e/g] [bedrag] → zet inkoopvergoeding
/ode [e/g] [bedrag] → zet ODE
/eb [e/g] [bedrag] → zet EnergieBelasting
/sp [k/o/a] → prijzen kaal, opslag, all-in
/verwijder → verwijder gebruiker
"""
# /hoger is helaas ff kapot

    @staticmethod
    def afmelden_help()->str:
        return """
Als je je afmeldt dan worden je gegevens verwijderd
Je krijgt geen automatische meldingen meer
Je kan de bot nog wel steeds gebruiken
"""

    @staticmethod
    def aanmelden_help()->str:
        return """
Als je je aanmeldt krijg je automatisch:
Een ochtend melding met hoogste en laagste prijs van de dag
De middag melding met de prijzen voor morgen
Een melding wanneer de prijs 0 of lager wordt
"""

    @staticmethod
    def donatie_help():
        return """
Het heeft me best wat tijd gekost om deze Bot te bouwen

Ook steek ik tijd in het fixen van Bugs en het bouwen van nieuwe zaken

Daarnaast draait het op een server die ook niet gratis is

Iedere donatie is dus van harte welkom

/donatie"""


    @staticmethod
    def get_name(update: telegram.Update,)->str:
        first_name = ""
        username = ""
        try:
            username = update.channel_post.sender_chat.title
        except Exception:
            pass

        try:
            first_name = update.message.chat.first_name
        except Exception:
            pass

        try:
            username = update.message.chat.username
        except Exception:
            pass

        if first_name is None or first_name == "":
            return username
        else:
            return first_name
