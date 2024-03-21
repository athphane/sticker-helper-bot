import ast
import os
import sys
from configparser import ConfigParser
from functools import wraps
from typing import BinaryIO, List, Optional, Union

from pyrogram import Client, types
from pyrogram.raw.all import layer
from pyrogram.types import CallbackQuery, Message

from stickerbot.helpers.sticker_state_enum import StickerStates


class StickerBot(Client):
    def __init__(self):
        self.STICKER_STATE = StickerStates.NOTHING
        self.STICKER_ID = None
        self.ERROR_MESSAGE_ID = None
        self.TAG_STRING = None
        self.EMOJI_STRING = None

        config_file = 'config.ini'

        self.config = config = ConfigParser()
        config.read(config_file)

        super().__init__(
            'stickerbot',
            api_id=config.getint('pyrogram', 'api_id'),
            api_hash=config.get('pyrogram', 'api_hash'),
            bot_token=config.get('pyrogram', 'bot_token'),
            workers=32,
            plugins=dict(root="stickerbot/plugins"),
            workdir="./"
        )

    def __str__(self):
        """
        String representation of the class object
        """
        return self.__class__.__name__

    async def start(self):
        await super().start()
        me = await self.get_me()
        print(f"{self.__class__.__name__} started on @{me.username}")

    async def stop(self, *args):
        """
        Stop function
        :param args:
        """
        await super().stop()
        print(f"{self.__class__.__name__} stopped. Bye.")

    def set_sticker_state(self, state: StickerStates):
        self.STICKER_STATE = state

    def get_sticker_state(self) -> StickerStates:
        return self.STICKER_STATE

    def set_sticker_id(self, sticker_id: str | None):
        self.STICKER_ID = sticker_id

    def get_sticker_id(self) -> str:
        return self.STICKER_ID

    def set_error_message_id(self, message_id: int | None):
        self.ERROR_MESSAGE_ID = message_id

    def get_error_message_id(self) -> int:
        return self.ERROR_MESSAGE_ID

    def set_tag(self, tag_string: str | None):
        self.TAG_STRING = tag_string

    def get_tag(self) -> str:
        return self.TAG_STRING

    def set_emoji(self, emoji_string: str | None):
        self.EMOJI_STRING = emoji_string

    def get_emoji(self) -> str:
        return self.EMOJI_STRING

