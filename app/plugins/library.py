import logging

from pyrogram import filters
from pyrogram.types import Message, CallbackQuery

from app import StickerBot
from app.helpers.sticker_manager import StickerManager
from app.helpers.sticker_state_enum import StickerStates
from app.helpers.keyboard_utils import (
    get_browse_keyboard,
    get_edit_existing_sticker_keyboard,
    get_main_keyboard,
)

LOGS = logging.getLogger(__name__)

# Per-user browse sessions. Kept in memory only; a restart simply ends the session.
BROWSE_STATES = {}


async def _safe_delete(bot: StickerBot, chat_id: int, message_id):
    if not message_id:
        return
    try:
        await bot.delete_messages(chat_id, message_id)
    except Exception as e:
        LOGS.debug(f"Could not delete message {message_id}: {e}")


async def _render_page(bot: StickerBot, user_id: int, chat_id: int):
    state = BROWSE_STATES[user_id]
    stickers = state['stickers']
    index = state['index']
    sticker = stickers[index]

    await _safe_delete(bot, chat_id, state.get('info_msg_id'))
    await _safe_delete(bot, chat_id, state.get('sticker_msg_id'))

    tags = sticker.get('tags') or []
    tags_display = ', '.join(tags) if tags else 'No tags'
    info_text = (
        f"Sticker {index + 1} of {len(stickers)}\n"
        f"Tags: {tags_display}\n"
        f"Emoji: {sticker.get('emoji') or 'None'}"
    )

    info_msg = await bot.send_message(chat_id, info_text)
    sticker_msg = await bot.send_sticker(chat_id, sticker['sticker_id'], reply_markup=get_browse_keyboard())

    state['info_msg_id'] = info_msg.id
    state['sticker_msg_id'] = sticker_msg.id


@StickerBot.on_message(filters.command("random") | filters.regex(r'^Random Sticker$'), group=-1)
async def random_sticker(bot: StickerBot, message: Message):
    user_id = message.from_user.id

    sticker = StickerManager.get_random_sticker(user_id)
    if not sticker:
        await message.reply_text("You have no stickers yet. Send me some to save!", reply_markup=get_main_keyboard())
        return

    await message.reply_sticker(sticker['sticker_id'])


@StickerBot.on_message(filters.command("collection") | filters.regex(r'^My Collection$'), group=-1)
async def show_collection(bot: StickerBot, message: Message):
    user_id = message.from_user.id

    stickers = StickerManager.find_stickers_by_user(user_id)
    if not stickers:
        await message.reply_text(
            "You have no stickers saved yet. Send me some to start your collection!",
            reply_markup=get_main_keyboard()
        )
        return

    BROWSE_STATES[user_id] = {
        'stickers': stickers,
        'index': 0,
        'info_msg_id': None,
        'sticker_msg_id': None,
    }
    await _render_page(bot, user_id, message.chat.id)


@StickerBot.on_callback_query(filters.regex(r'^browse_(prev|next)$'))
async def browse_navigate(bot: StickerBot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    state = BROWSE_STATES.get(user_id)
    if not state or not state['stickers']:
        await callback_query.answer("Browse session expired. Use /collection to start again.")
        return

    total = len(state['stickers'])
    if callback_query.data == 'browse_prev':
        state['index'] = (state['index'] - 1) % total
    else:
        state['index'] = (state['index'] + 1) % total

    await _render_page(bot, user_id, callback_query.message.chat.id)
    await callback_query.answer()


@StickerBot.on_callback_query(filters.regex(r'^browse_delete$'))
async def browse_delete(bot: StickerBot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    state = BROWSE_STATES.get(user_id)
    if not state or not state['stickers']:
        await callback_query.answer("Browse session expired. Use /collection to start again.")
        return

    chat_id = callback_query.message.chat.id
    sticker = state['stickers'][state['index']]

    try:
        StickerManager.delete_sticker(user_id, sticker['sticker_unique_id'])
    except ValueError as e:
        LOGS.error(f"ValueError during browse delete: {e}")
        await callback_query.answer("Delete failed")
        return

    state['stickers'].pop(state['index'])

    if not state['stickers']:
        await _safe_delete(bot, chat_id, state.get('info_msg_id'))
        await _safe_delete(bot, chat_id, state.get('sticker_msg_id'))
        BROWSE_STATES.pop(user_id, None)
        await bot.send_message(chat_id, "Sticker deleted. Your collection is now empty.", reply_markup=get_main_keyboard())
    else:
        if state['index'] >= len(state['stickers']):
            state['index'] = len(state['stickers']) - 1
        await _render_page(bot, user_id, chat_id)

    await callback_query.answer("Sticker deleted")


@StickerBot.on_callback_query(filters.regex(r'^browse_edit$'))
async def browse_edit(bot: StickerBot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    state = BROWSE_STATES.get(user_id)
    if not state or not state['stickers']:
        await callback_query.answer("Browse session expired. Use /collection to start again.")
        return

    chat_id = callback_query.message.chat.id
    sticker = state['stickers'][state['index']]

    await _safe_delete(bot, chat_id, state.get('info_msg_id'))
    await _safe_delete(bot, chat_id, state.get('sticker_msg_id'))
    BROWSE_STATES.pop(user_id, None)

    bot.set_sticker_id(user_id, sticker['sticker_id'])
    bot.set_sticker_unique_id(user_id, sticker['sticker_unique_id'])
    bot.set_sticker_state(user_id, StickerStates.EDITING_EXISTING_STICKER)

    await bot.send_message(
        chat_id,
        "What would you like to edit on this sticker?",
        reply_markup=get_edit_existing_sticker_keyboard()
    )
    await callback_query.answer("Edit sticker")


@StickerBot.on_callback_query(filters.regex(r'^browse_close$'))
async def browse_close(bot: StickerBot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    state = BROWSE_STATES.get(user_id)
    if state:
        await _safe_delete(bot, callback_query.message.chat.id, state.get('info_msg_id'))
        await _safe_delete(bot, callback_query.message.chat.id, state.get('sticker_msg_id'))
        BROWSE_STATES.pop(user_id, None)
    await callback_query.answer("Closed")
