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

SUPABASE_URL = config.get('supabase', 'url')
SUPABASE_KEY = config.get('supabase', 'key')

# Global Variables
client = None
