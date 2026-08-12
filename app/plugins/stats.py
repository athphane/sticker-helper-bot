import logging

from pyrogram import filters
from pyrogram.types import Message

from app import StickerBot
from app.helpers.sticker_manager import StickerManager
from app.helpers.keyboard_utils import get_main_keyboard

LOGS = logging.getLogger(__name__)

TOP_N = 5


def _format_sticker_line(index: int, sticker: dict) -> str:
    tags = sticker.get('tags') or []
    tags_display = ', '.join(tags) if tags else 'no tags'
    emoji = sticker.get('emoji') or ''
    uses = sticker.get('use_count') or 0
    return f"{index}. {emoji} <b>{tags_display}</b> — {uses} uses"


@StickerBot.on_message(filters.command("stats"))
async def show_stats(bot: StickerBot, message: Message):
    user_id = message.from_user.id

    stats = StickerManager.get_stats(user_id, limit=TOP_N)

    if not stats["total_stickers"]:
        await message.reply_text(
            "You have no stickers saved yet. Send me some to start building your stats!",
            reply_markup=get_main_keyboard()
        )
        return

    lines = [
        "📊 <b>Your Sticker Stats</b>",
        "",
        f"Stickers saved: <b>{stats['total_stickers']}</b>",
        f"Stickers with tags: <b>{stats['tagged_stickers']}</b>",
        f"Total sends (inline): <b>{stats['total_uses']}</b>",
    ]

    most_used = stats["most_used_stickers"]
    if most_used:
        lines.append("")
        lines.append("🔥 <b>Most used stickers</b>")
        lines.extend(_format_sticker_line(i, s) for i, s in enumerate(most_used, 1))

    most_used_tags = stats["most_used_tags"]
    if most_used_tags:
        lines.append("")
        lines.append("🏷️ <b>Most used tags</b>")
        lines.extend(f"{i}. <b>{t['_id']}</b> — {t['uses']} uses" for i, t in enumerate(most_used_tags, 1))

    most_used_emojis = stats["most_used_emojis"]
    if most_used_emojis:
        lines.append("")
        lines.append("😀 <b>Most used emojis</b>")
        lines.extend(f"{i}. {e['_id']} — {e['uses']} uses" for i, e in enumerate(most_used_emojis, 1))

    await message.reply_text("\n".join(lines), reply_markup=get_main_keyboard())
