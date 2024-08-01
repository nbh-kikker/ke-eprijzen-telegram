import sys
import os
# import yaml
import configparser

from resources.dispatcher import Dispatcher

import logging
import logging.config

dir_path = os.path.dirname(os.path.realpath(__file__))

config_folder = None
log_folder = None
os.environ['TZ'] = 'Europe/Amsterdam'

PY_ENV = os.getenv('PY_ENV', 'dev')

match PY_ENV:
    case 'dev':
        config_filename = "development.ini"
        config_folder = os.path.join(dir_path, "..","config")
        log_folder = os.path.join(dir_path, "..", "logging")
        graphs_folder = os.path.join(dir_path, "..", "..", "graphs")

        logging.config.fileConfig(os.path.join(config_folder, 'logging.conf'))
        log = logging.getLogger(PY_ENV)
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
    case 'prod':
        config_filename = "production.ini"
        config_folder = os.path.join(dir_path, 'config')
        log_folder = os.path.join(dir_path, "logging")
        graphs_folder = os.path.join(dir_path, "graphs")

        logging.config.fileConfig(os.path.join(config_folder, 'logging.conf'))
        log = logging.getLogger(PY_ENV)
        logger = logging.getLogger()
        logger.setLevel(logging.ERROR)
    case _:
        pass

def check_file(file:str = "")->bool:
    if os.path.exists(file):
        return True
    return False

try:
    config_file = os.path.join(config_folder, config_filename)
    if not check_file(file=config_file):
        raise Exception(f"Config file not found : {config_file}")
except Exception as e:
    log.critical(e, exc_info=True)
    sys.exit(e)

config = None
try:
    # with open(config_file, 'r') as file:
    config = configparser.ConfigParser()
    config.read(config_file)
        # config = yaml.safe_load(file)
except Exception as e:
    log.critical(e, exc_info=True)
    sys.exit(e)

ip = config["API"]["ip"]
port = config["API"]["port"]

if __name__ == "__main__":
    # verwerk direct bij opstart
    D = Dispatcher(config=config)
    D.start_dispatch()