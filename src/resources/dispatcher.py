import os
# import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, PreCheckoutQueryHandler
from resources.dispatcher_functions import Dispatcher_Functions
from telegram.ext.filters import Filters

import logging

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class Dispatcher(Dispatcher_Functions):
    def __init__(self,*args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def start_dispatch(self)->None:
        try:
            u = Updater(self.telegram_key, use_context=True)
            j = u.job_queue

            # run every minute
            job_minute = j.run_repeating(self.auto_bot, interval=60, first=1) #iedere minuut

            start_handler = CommandHandler('start', self.start_me_up)
            u.dispatcher.add_handler(start_handler)

            aanmelden_handler = CommandHandler(['a','aanmelden'], self.aanmelden)
            u.dispatcher.add_handler(aanmelden_handler)

            afmelden_handler = CommandHandler(['afmelden','verwijderme', 'verwijder'], self.verwijderme)
            u.dispatcher.add_handler(afmelden_handler)

            instellingen_handler = CommandHandler(['i','instellingen'], self.instellingen)
            u.dispatcher.add_handler(instellingen_handler)

            ochtend_handler = CommandHandler(['o','ochtend'], self.ochtend_instellen)
            u.dispatcher.add_handler(ochtend_handler)

            middag_handler = CommandHandler(['m','middag'], self.middag_instellen)
            u.dispatcher.add_handler(middag_handler)

            ldinstellen_handler = CommandHandler(['ld','lagerdan', 'lager'], self.ld_instellen)
            u.dispatcher.add_handler(ldinstellen_handler)

            koa_handler = CommandHandler(['koa', 'soortprijs', 'sp'], self.soort_prijs_instellen)
            u.dispatcher.add_handler(koa_handler)

            user_api_handler = CommandHandler(['api'], self.user_api_data)
            u.dispatcher.add_handler(user_api_handler)

            api_key_handler = CommandHandler(['apikey'], self.api_key)
            u.dispatcher.add_handler(api_key_handler)

            opslaginstellen_handler = CommandHandler(['iv', 'opslag','inkoopvergoeding'], self.opslag_instellen)
            u.dispatcher.add_handler(opslaginstellen_handler)

            odeinstellen_handler = CommandHandler(['ode'], self.ode_instellen)
            u.dispatcher.add_handler(odeinstellen_handler)

            ebinstellen_handler = CommandHandler(['eb'], self.eb_instellen)
            u.dispatcher.add_handler(ebinstellen_handler)

            current_handler = CommandHandler('nu', self.show_current)
            u.dispatcher.add_handler(current_handler)

            today_handler = CommandHandler('vandaag', self.show_today)
            u.dispatcher.add_handler(today_handler)

            tomorrow_handler = CommandHandler('morgen', self.show_tomorrow)
            u.dispatcher.add_handler(tomorrow_handler)

            past_handler = CommandHandler('verleden', self.show_past)
            u.dispatcher.add_handler(past_handler)

            locale_handler = CommandHandler(['locale','locatie'], self.set_locale)
            u.dispatcher.add_handler(locale_handler)

            onderhoud_handler = CommandHandler('onderhoud', self.onderhoud)
            u.dispatcher.add_handler(onderhoud_handler)

            bericht_handler = CommandHandler('bericht', self.bericht)
            u.dispatcher.add_handler(bericht_handler)

            help_handler = CommandHandler(['h', 'help', 'hulp'], self.help)
            u.dispatcher.add_handler(help_handler)

            help_handler = CommandHandler(['l', 'login', 'login'], self.login)
            u.dispatcher.add_handler(help_handler)

            donate_handler = CommandHandler(['d','doneer', 'donatie', 'doneren'], self.donate)
            u.dispatcher.add_handler(donate_handler)

            system_handler = CommandHandler(['s', 'system', 'systeem'], self.systeminfo)
            u.dispatcher.add_handler(system_handler)

            upgrade_tokens_handler = CommandHandler(['ut'], self.upgrade_tokens)
            u.dispatcher.add_handler(upgrade_tokens_handler)

            # # Payments
            # pre_chechout_handler = PreCheckoutQueryHandler(self.pre_checkout_handler)
            # u.dispatcher.add_handler(pre_chechout_handler)

            # opwaarderen_handler = CommandHandler(['op', 'opwaarderen'], self.opwaarderen)
            # u.dispatcher.add_handler(opwaarderen_handler)

            # successfull_pay_handler = MessageHandler(Filters._SuccessfulPayment, self.successful_payment_callback)
            # u.dispatcher.add_handler(successfull_pay_handler)

            # anything else
            unknown_handler = MessageHandler(Filters.command, self.help)
            u.dispatcher.add_handler(unknown_handler)

            blahblah_handler = MessageHandler(Filters.text, self.help)
            u.dispatcher.add_handler(blahblah_handler)


            # Start the Bot
            u.start_polling()
            u.idle()
        except Exception as e:
            log.error(e, exc_info=True)
            pass
