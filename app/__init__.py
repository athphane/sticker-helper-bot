import logging
from configparser import ConfigParser
from logging.handlers import TimedRotatingFileHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        TimedRotatingFileHandler('logs/app.log', when="midnight", encoding=None,
                                 delay=False, backupCount=10),
        logging.StreamHandler()
    ]
)
LOGS = logging.getLogger(__name__)

__version__ = '1.0.0'
__author__ = 'Athfan Khaleel'

config = ConfigParser()
config.read('config.ini')

TELEGRAM_API_ID = config.getint('telegram', 'api_id')
TELEGRAM_API_HASH = config.get('telegram', 'api_hash')
TELEGRAM_BOT_TOKEN = config.get('telegram', 'bot_token')
TELEGRAM_ADMINS = config.get('telegram', 'admins', fallback='').split(',')
TELEGRAM_ADMINS = [int(x.strip()) for x in TELEGRAM_ADMINS if x.strip()]

MONGO_URL = config.get('mongo', 'url')
MONGO_USERNAME = config.get('mongo', 'username')
MONGO_PASSWORD = config.get('mongo', 'password')
MONGO_DB_NAME = config.get('mongo', 'db_name', fallback='stickerbot')
MONGO_DB_AUTH_SOURCE = config.get('mongo', 'auth_source', fallback='')

from app.bot import StickerBot

StickerBot = StickerBot(__version__, api_id=TELEGRAM_API_ID, api_hash=TELEGRAM_API_HASH,
                        bot_token=TELEGRAM_BOT_TOKEN)
