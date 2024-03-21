from pyrogram import filters
from pyrogram.types import Message

from stickerbot import StickerBot


@StickerBot.on_message(filters.command(["start"]))
async def start(client: StickerBot, message: Message):
    await message.reply_text("Hi, I'm StickerBot.")


