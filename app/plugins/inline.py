from uuid import uuid4

from pyrogram.types import InlineQuery, InlineQueryResultArticle, InlineQueryResultCachedSticker, \
    InputTextMessageContent

from app import StickerBot
from app.database.user_db import UserDB
from app.helpers.sticker_manager import StickerManager

user_db = UserDB()

PAGE_SIZE = 50


@StickerBot.on_inline_query()
async def stickers_inline(bot: StickerBot, inline_query: InlineQuery):
    from_user = inline_query.from_user.id
    query = inline_query.query

    # Create or update user in database
    user_db.find_or_create(inline_query.from_user)

    offset = int(inline_query.offset) if inline_query.offset else 0
    stickers = StickerManager.all_stickers_like(query, from_user, limit=PAGE_SIZE, offset=offset)

    results = []
    next_offset = ""

    if not stickers and query:  # If no stickers found and a query was provided
        results.append(InlineQueryResultArticle(
            title="No stickers found",
            input_message_content=InputTextMessageContent(f'No stickers found for "{query}"'),
        ))
    elif not stickers:  # If no stickers found but no query provided (showing all)
        results.append(InlineQueryResultArticle(
            title="No stickers saved yet",
            input_message_content=InputTextMessageContent('You have no stickers saved yet. Send some stickers to the bot to start saving them!'),
        ))
    else:
        for sticker in stickers:
            results.append(InlineQueryResultCachedSticker(
                sticker_file_id=sticker['sticker_id'],
                id=str(uuid4()),
            ))
        if len(stickers) == PAGE_SIZE:
            next_offset = str(offset + PAGE_SIZE)

    await inline_query.answer(results, cache_time=1, is_personal=True, is_gallery=True, next_offset=next_offset)
