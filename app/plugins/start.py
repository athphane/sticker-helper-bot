from pyrogram import filters
from pyrogram.types import Message

from app import StickerBot
from app.database.user_db import UserDB
from app.helpers.sticker_manager import StickerManager
from app.helpers.keyboard_utils import get_main_keyboard

user_db = UserDB()


@StickerBot.on_message(filters.command(["start"]))
async def start(client: StickerBot, message: Message):
    # Create or update user in database
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


HELP_TEXT = (
    "Here's how to use me:\n\n"
    "1. Send me any sticker and I'll save it to your personal collection.\n"
    "2. Add tags (words separated by commas) and an emoji so you can find it later.\n"
    "3. In any chat, type @stickerdexbot and your search terms to find and send your stickers.\n\n"
    "Commands:\n"
    "/start - Show this info\n"
    "/help - Show this help\n"
    "/clear - Reset the current save/edit process\n"
    "/stats - See your most-used stickers, tags and emojis\n\n"
    "Tips:\n"
    "- Send a sticker you've already saved to edit its tags/emoji or delete it.\n"
    "- After saving, you can add more tags to the sticker.\n"
    "- Type @stickerdexbot with no query to browse your whole collection."
)


@StickerBot.on_message(filters.command(["help"]))
async def help_command(client: StickerBot, message: Message):
    await message.reply_text(HELP_TEXT, reply_markup=get_main_keyboard())


