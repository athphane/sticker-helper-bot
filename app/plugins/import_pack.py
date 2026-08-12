import logging
import re

from pyrogram import filters
from pyrogram.types import Message

from app import StickerBot
from app.database.user_db import UserDB
from app.helpers.sticker_manager import StickerManager
from app.helpers.keyboard_utils import get_main_keyboard

LOGS = logging.getLogger(__name__)

user_db = UserDB()

PACK_LINK_RE = re.compile(r'(?:t\.me|telegram\.me)/addstickers/([A-Za-z0-9_]+)', re.IGNORECASE)


@StickerBot.on_message(
    filters.command("import") | filters.regex(r'(?:t\.me|telegram\.me)/addstickers/'),
    group=-1
)
async def import_pack(bot: StickerBot, message: Message):
    user_id = message.from_user.id
    user_db.find_or_create(message.from_user)

    text = message.text or message.caption or ''
    match = PACK_LINK_RE.search(text)
    if not match:
        await message.reply_text(
            "Send me a sticker pack link like:\nhttps://t.me/addstickers/PackName",
            reply_markup=get_main_keyboard()
        )
        return

    pack_name = match.group(1)
    status = await message.reply_text(f"Importing stickers from '{pack_name}'...")

    try:
        stickers = await bot.get_stickers(pack_name)
    except Exception as e:
        LOGS.warning(f"Could not fetch sticker pack '{pack_name}': {e}")
        await status.edit_text(
            f"Couldn't find the sticker pack '{pack_name}'. Check the link and try again.",
            reply_markup=get_main_keyboard()
        )
        return

    if not stickers:
        await status.edit_text(f"The sticker pack '{pack_name}' is empty.", reply_markup=get_main_keyboard())
        return

    imported = 0
    skipped = 0
    for sticker in stickers:
        if StickerManager.sticker_exists(user_id, sticker.file_unique_id):
            skipped += 1
            continue
        StickerManager.insert_sticker(
            user_id,
            sticker.file_id,
            sticker.file_unique_id,
            [pack_name],
            sticker.emoji or ''
        )
        imported += 1

    summary = f"Done! Imported {imported} new stickers from '{pack_name}'."
    if skipped:
        summary += f" {skipped} were already saved."
    await status.edit_text(summary, reply_markup=get_main_keyboard())
