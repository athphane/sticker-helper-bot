from uuid import uuid4

from pyrogram.types import InlineQuery, InlineQueryResultArticle, InlineQueryResultCachedSticker, \
    InputTextMessageContent

from app import StickerBot
from app.database.user_db import UserDB
from app.helpers.sticker_manager import StickerManager

user_db = UserDB()


@StickerBot.on_inline_query()
async def stickers_inline(bot: StickerBot, inline_query: InlineQuery):
    from_user = inline_query.from_user.id
    query = inline_query.query

    results = []

    # Create or update user in database
    user_db.find_or_create(inline_query.from_user)

    # Get stickers for the specific user, remove admin restriction
    stickers_result = StickerManager.all_stickers_like(query, from_user)
    stickers = stickers_result['data']

    if not stickers and query:  # If no stickers found and a query was provided
        article = InlineQueryResultArticle(
            title="No stickers found",
            input_message_content=InputTextMessageContent(f'No stickers found for "{query}"'),
        )
        results.append(article)
    elif not stickers:  # If no stickers found but no query provided (showing all)
        article = InlineQueryResultArticle(
            title="No stickers saved yet",
            input_message_content=InputTextMessageContent('You have no stickers saved yet. Send some stickers to the bot to start saving them!'),
        )
        results.append(article)
    else:
        for sticker in stickers:
            article = InlineQueryResultCachedSticker(
                sticker_file_id=sticker['sticker_id'],
                id=str(uuid4()),
            )
            results.append(article)

    await inline_query.answer(results, cache_time=1, is_gallery=True)
