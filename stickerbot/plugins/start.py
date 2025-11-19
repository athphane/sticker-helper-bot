from pyrogram import filters
from pyrogram.types import Message

from stickerbot import StickerBot
from stickerbot.database.user_db import UserDB
from stickerbot.helpers.sticker_manager import StickerManager
from stickerbot.helpers.keyboard_utils import get_main_keyboard


@StickerBot.on_message(filters.command(["start"]))
async def start(client: StickerBot, message: Message):
    # Create or update user in database
    user_db = UserDB()
    user_db.find_or_create(message.from_user)

    # Get user's sticker count
    sticker_count = StickerManager.get_user_sticker_count(message.from_user.id)

    welcome_message = (
        f"Hi {message.from_user.first_name}, I'm StickerBot! 🤖\n\n"
        f"You currently have {sticker_count} stickers saved.\n\n"
        "To save stickers:\n"
        "1. Send me a sticker\n"
        "2. I'll ask for a tag\n"
        "3. Then an emoji\n"
        "4. Use @botname in any chat to search and send your stickers!"
    )

    await message.reply_text(welcome_message, reply_markup=get_main_keyboard())


