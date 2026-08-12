import logging

from pyrogram import Client
from pyrogram.raw.all import layer
from pyrogram.types import BotCommand, BotCommandScopeDefault

from app.database import close_connection
from app.database.state_db import StateDB
from app.helpers.sticker_state_enum import StickerStates

LOGS = logging.getLogger(__name__)

# One StateDB accessor reused process-wide (its backing client is a shared singleton).
_state_db = StateDB()

_DEFAULT_STATE = {
    'state': StickerStates.NOTHING,
    'sticker_id': None,           # Actual file ID for sending the sticker
    'sticker_unique_id': None,    # Unique ID for duplicate detection
    'error_message_id': None,
    'tag_string': None,
    'emoji_string': None
}


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

    async def start(self, **kwargs):
        await super().start(**kwargs)

        await self.set_bot_commands(
            [
                BotCommand('start', 'Start the bot'),
                BotCommand('help', 'How to use the bot'),
                BotCommand('clear', 'Reset the current process'),
                BotCommand('random', 'Send a random sticker from your collection'),
                BotCommand('collection', 'Browse your saved stickers'),
                BotCommand('import', 'Import a sticker pack by link'),
                BotCommand('stats', 'See your sticker statistics'),
            ],
            scope=BotCommandScopeDefault()
        )

        me = await self.get_me()
        LOGS.info(f"{self.__class__.__name__} v{self.version} (Layer {layer}) started on @{me.username}.\n"
                  f"Your Bot is ready to serve.")

    async def stop(self, *args, **kwargs):
        await super().stop(*args, **kwargs)
        close_connection()
        LOGS.info(f"{self.__class__.__name__} stopped. Bye.")

    def _get_user_state(self, user_id: int):
        """Load a user's workflow state from memory, falling back to MongoDB."""
        if user_id not in self.USER_STATES:
            state = _state_db.load(user_id)
            if state is None:
                state = dict(_DEFAULT_STATE)
            else:
                defaults = dict(_DEFAULT_STATE)
                defaults.update(state)
                state = defaults
            self.USER_STATES[user_id] = state
        return self.USER_STATES[user_id]

    def _persist_user_state(self, user_id: int):
        """Write a user's in-memory state back to MongoDB."""
        _state_db.save(user_id, self.USER_STATES[user_id])

    def clear_user_state(self, user_id: int):
        """Drop a user's workflow state from MongoDB and memory."""
        self.USER_STATES.pop(user_id, None)
        _state_db.delete(user_id)

    def set_sticker_state(self, user_id: int, state: StickerStates):
        user_state = self._get_user_state(user_id)
        user_state['state'] = state
        self._persist_user_state(user_id)

    def get_sticker_state(self, user_id: int) -> StickerStates:
        user_state = self._get_user_state(user_id)
        return user_state['state']

    def set_sticker_id(self, user_id: int, sticker_id: str | None):
        user_state = self._get_user_state(user_id)
        user_state['sticker_id'] = sticker_id
        self._persist_user_state(user_id)

    def get_sticker_id(self, user_id: int) -> str:
        user_state = self._get_user_state(user_id)
        return user_state['sticker_id']

    def set_sticker_unique_id(self, user_id: int, sticker_unique_id: str | None):
        user_state = self._get_user_state(user_id)
        user_state['sticker_unique_id'] = sticker_unique_id
        self._persist_user_state(user_id)

    def get_sticker_unique_id(self, user_id: int) -> str:
        user_state = self._get_user_state(user_id)
        return user_state['sticker_unique_id']

    def set_error_message_id(self, user_id: int, message_id: int | None):
        user_state = self._get_user_state(user_id)
        user_state['error_message_id'] = message_id
        self._persist_user_state(user_id)

    def get_error_message_id(self, user_id: int) -> int:
        user_state = self._get_user_state(user_id)
        return user_state['error_message_id']

    def set_tag(self, user_id: int, tag_string: str | list | None):
        user_state = self._get_user_state(user_id)
        user_state['tag_string'] = tag_string
        self._persist_user_state(user_id)

    def get_tag(self, user_id: int) -> str | list:
        user_state = self._get_user_state(user_id)
        return user_state['tag_string']

    def set_emoji(self, user_id: int, emoji_string: str | None):
        user_state = self._get_user_state(user_id)
        user_state['emoji_string'] = emoji_string
        self._persist_user_state(user_id)

    def get_emoji(self, user_id: int) -> str:
        user_state = self._get_user_state(user_id)
        return user_state['emoji_string']
