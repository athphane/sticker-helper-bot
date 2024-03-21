import json
from uuid import uuid4

from pyrogram.types import InlineQuery, InlineQueryResultArticle, InlineQueryResultCachedSticker, \
    InputTextMessageContent

from stickerbot import StickerBot, ADMIN
from stickerbot.helpers.sticker_manager import StickerManager


@StickerBot.on_inline_query()
async def stickers_inline(bot: StickerBot, inline_query: InlineQuery):
    from_user = inline_query.from_user.id

    results = []
    query = inline_query.query

    if from_user != int(ADMIN):
        article = InlineQueryResultArticle(
            title="Go Away",
            input_message_content=InputTextMessageContent('Unauthorized access.'),
        )
        results.append(article)
        await inline_query.answer(results, cache_time=1)
        return

    if not query:
        stickers = StickerManager().all_stickers_like(query).json()
        stickers = json.loads(stickers)['data']
        for sticker in stickers:
            article = InlineQueryResultCachedSticker(
                sticker_file_id=sticker['sticker_id'],
                id=str(uuid4()),
            )
            print(article)
            results.append(article)

    if query:
        stickers = StickerManager().all_stickers_like(query).json()
        stickers = json.loads(stickers)['data']
        for sticker in stickers:
            article = InlineQueryResultCachedSticker(
                sticker_file_id=sticker['sticker_id'],
                id=str(uuid4()),
            )
            results.append(article)

    await inline_query.answer(results, cache_time=1, is_gallery=True)
