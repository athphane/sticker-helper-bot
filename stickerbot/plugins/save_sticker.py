from pyrogram import filters
from pyrogram.types import Message

from stickerbot import StickerBot
from stickerbot.helpers.sticker_manager import StickerManager
from stickerbot.helpers.sticker_state_enum import StickerStates
from stickerbot.helpers.string_parsers import is_text, is_emoji


@StickerBot.on_message(filters.command(["clear"]))
async def reset_state(bot: StickerBot, message: Message):
    bot.set_sticker_state(StickerStates.NOTHING)
    bot.set_tag(None)
    bot.set_emoji(None)
    bot.set_error_message_id(None)
    await message.reply_text("State reset.")


@StickerBot.on_message(filters.sticker)
async def incoming_sticker(bot: StickerBot, message: Message):
    if bot.get_sticker_state() is not StickerStates.NOTHING:
        if bot.get_error_message_id() is not None:
            await bot.delete_messages(message.chat.id, bot.get_error_message_id())

    if bot.get_sticker_state() == StickerStates.WAITING_FOR_TAG:
        await message.delete()
        new_error_message = await message.reply_text(
            "You need to send me the tag for the sticker you sent previously.\nIf you want to stop adding, "
            "send the /clear command")
        bot.set_error_message_id(new_error_message.id)
        return

    if bot.get_sticker_state() == StickerStates.WAITING_FOR_EMOJI:
        await message.delete()
        new_error_message = await message.reply_text(
            "You need to send me the emoji for the sticker you sent previously.\nIf you want to stop adding, "
            "send the /clear command")
        bot.set_error_message_id(new_error_message.id)
        return

    bot.set_sticker_id(message.sticker.file_id)
    bot.set_sticker_state(StickerStates.WAITING_FOR_TAG)

    await message.reply_text("You sent a sticker!\nSend me the tag for this sticker.")


@StickerBot.on_message(filters.regex(r'^(?!/)') & filters.text)
async def set_tag(bot: StickerBot, message: Message):
    if bot.get_sticker_state() is StickerStates.WAITING_FOR_TAG:

        if is_text(message.text):
            bot.set_sticker_state(StickerStates.WAITING_FOR_EMOJI)
            bot.set_tag(message.text)
            await message.reply_text(
                "You sent a tag for the sticker!\nSend me the emoji for this sticker.",
                reply_to_message_id=message.id,
            )
            return

    if bot.get_sticker_state() is StickerStates.WAITING_FOR_EMOJI:
        if is_emoji(message.text):
            bot.set_sticker_state(StickerStates.SAVING_STICKER)
            bot.set_emoji(message.text)
            await message.reply_text("You sent an emoji for the sticker!\nI'm saving the sticker now.")
            await handle_sticker_saving(bot, message)
        else:
            await message.reply_text("You need to send me an emoji for the sticker you sent previously.\nIf you want to"
                                     "stop adding, send the /clear command")
            return


async def handle_sticker_saving(bot: StickerBot, message: Message):
    sticker_id = bot.get_sticker_id()
    tag_string = bot.get_tag()
    emoji_string = bot.get_emoji()

    response = StickerManager.insert_sticker(sticker_id, tag_string, emoji_string)
    if response.data is not None:
        print(response.data)
        await message.reply_text("Sticker saved successfully!")
    else:
        await message.reply_text("Sticker saving failed!")

    bot.set_sticker_state(StickerStates.NOTHING)
