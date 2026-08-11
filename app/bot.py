import logging

from pyrogram import Client
from pyrogram.raw.all import layer
from pyrogram.types import BotCommand, BotCommandScopeDefault

from app.database import close_connection
from app.helpers.sticker_state_enum import StickerStates

LOGS = logging.getLogger(__name__)


class StickerBot(Client):
    def __init__(self, version='0.0.0', **kwargs):
        self.version = version
        self.USER_STATES = {}

        super().__init__(
            'stickerbot',
            api_id=kwargs['api_id'],
            api_hash=kwargs['api_hash'],
            bot_token=kwargs['bot_token'],
            workers=16,
            plugins=dict(root="app/plugins"),
            workdir="./workdir"
        )

    def __str__(self):
        """
        String representation of the class object
        """
        return self.__class__.__name__

    async def start(self):
        await super().start()

        await self.set_bot_commands(
            [
                BotCommand('start', 'Start the bot'),
                BotCommand('clear', 'Reset the current process'),
            ],
            scope=BotCommandScopeDefault()
        )

        me = await self.get_me()
        LOGS.info(f"{self.__class__.__name__} v{self.version} (Layer {layer}) started on @{me.username}.\n"
                  f"Your Bot is ready to serve.")

    async def stop(self, *args):
        await super().stop()
        close_connection()
        LOGS.info(f"{self.__class__.__name__} stopped. Bye.")

    def _get_user_state(self, user_id: int):
        """Get or create state for a specific user"""
        if user_id not in self.USER_STATES:
            self.USER_STATES[user_id] = {
                'state': StickerStates.NOTHING,
                'sticker_id': None,           # Actual file ID for sending the sticker
                'sticker_unique_id': None,    # Unique ID for duplicate detection
                'error_message_id': None,
                'tag_string': None,
                'emoji_string': None
            }
        return self.USER_STATES[user_id]

    def set_sticker_state(self, user_id: int, state: StickerStates):
        user_state = self._get_user_state(user_id)
        user_state['state'] = state

    def get_sticker_state(self, user_id: int) -> StickerStates:
        user_state = self._get_user_state(user_id)
        return user_state['state']

    def set_sticker_id(self, user_id: int, sticker_id: str | None):
        user_state = self._get_user_state(user_id)
        user_state['sticker_id'] = sticker_id

    def get_sticker_id(self, user_id: int) -> str:
        user_state = self._get_user_state(user_id)
        return user_state['sticker_id']

    def set_sticker_unique_id(self, user_id: int, sticker_unique_id: str | None):
        user_state = self._get_user_state(user_id)
        user_state['sticker_unique_id'] = sticker_unique_id

    def get_sticker_unique_id(self, user_id: int) -> str:
        user_state = self._get_user_state(user_id)
        return user_state['sticker_unique_id']

    def set_error_message_id(self, user_id: int, message_id: int | None):
        user_state = self._get_user_state(user_id)
        user_state['error_message_id'] = message_id

    def get_error_message_id(self, user_id: int) -> int:
        user_state = self._get_user_state(user_id)
        return user_state['error_message_id']

    def set_tag(self, user_id: int, tag_string: str | list | None):
        user_state = self._get_user_state(user_id)
        user_state['tag_string'] = tag_string

    def get_tag(self, user_id: int) -> str | list:
        user_state = self._get_user_state(user_id)
        return user_state['tag_string']

    def set_emoji(self, user_id: int, emoji_string: str | None):
        user_state = self._get_user_state(user_id)
        user_state['emoji_string'] = emoji_string

    def get_emoji(self, user_id: int) -> str:
        user_state = self._get_user_state(user_id)
        return user_state['emoji_string']
