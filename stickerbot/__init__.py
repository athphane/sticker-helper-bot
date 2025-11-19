import logging
from configparser import ConfigParser
from logging.handlers import TimedRotatingFileHandler

from stickerbot.stickerbot import StickerBot

# Logging at the start to catch everything
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        TimedRotatingFileHandler('logs/stickerbot.log', when="midnight", encoding=None,
                                 delay=False, backupCount=10),
        logging.StreamHandler()
    ]
)
LOGS = logging.getLogger(__name__)

__author__ = 'Athfan Khaleel'

StickerBot = StickerBot()

# Read from config file
name = str(StickerBot).lower()
config_file = 'config.ini'
config = ConfigParser()
config.read(config_file)

# Get from config file.
ADMIN = config.get('pyrogram', 'admin')

MONGO_URL = config.get('mongodb', 'url')
MONGO_DB_NAME = config.get('mongodb', 'database', fallback='stickerbot')
MONGO_USERNAME = config.get('mongodb', 'username')
MONGO_PASSWORD = config.get('mongodb', 'password')

# Global Variables
client = None
