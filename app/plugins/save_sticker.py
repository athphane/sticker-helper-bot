from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from app import StickerBot
from app.database.user_db import UserDB
from app.helpers.sticker_manager import StickerManager
from app.helpers.sticker_state_enum import StickerStates
from app.helpers.string_parsers import is_text, is_emoji
from app.helpers.keyboard_utils import get_tag_keyboard, get_emoji_keyboard, get_common_emojis_keyboard, get_confirmation_keyboard, get_main_keyboard, get_edit_existing_sticker_keyboard

user_db = UserDB()


@StickerBot.on_message(filters.command(["clear"]))
async def reset_state(bot: StickerBot, message: Message):
    user_id = message.from_user.id
    bot.set_sticker_state(user_id, StickerStates.NOTHING)
    bot.set_tag(user_id, None)
    bot.set_emoji(user_id, None)
    bot.set_error_message_id(user_id, None)

    # Send the main keyboard after clearing
    await message.reply_text("State reset.", reply_markup=get_main_keyboard())


@StickerBot.on_message(filters.sticker)
async def incoming_sticker(bot: StickerBot, message: Message):
    user_id = message.from_user.id

    # Create or update user in database
    user_db.find_or_create(message.from_user)

    if bot.get_sticker_state(user_id) is not StickerStates.NOTHING:
        error_msg_id = bot.get_error_message_id(user_id)
        if error_msg_id is not None:
            await bot.delete_messages(message.chat.id, error_msg_id)

    if bot.get_sticker_state(user_id) == StickerStates.WAITING_FOR_TAG:
        await message.delete()
        new_error_message = await message.reply_text(
            "You need to send me the tag for the sticker you sent previously.\nIf you want to stop adding, "
            "send the /clear command")
        bot.set_error_message_id(user_id, new_error_message.id)
        return

    if bot.get_sticker_state(user_id) == StickerStates.WAITING_FOR_EMOJI:
        await message.delete()
        new_error_message = await message.reply_text(
            "You need to send me the emoji for the sticker you sent previously.\nIf you want to stop adding, "
            "send the /clear command")
        bot.set_error_message_id(user_id, new_error_message.id)
        return

    sticker_id = message.sticker.file_id
    sticker_unique_id = message.sticker.file_unique_id  # Get the unique ID for duplicate detection

    bot.set_sticker_id(user_id, sticker_id)
    bot.set_sticker_unique_id(user_id, sticker_unique_id)

    # Debug: Check if this sticker already exists for the user
    print(f"Checking if sticker exists - User: {user_id}, Sticker unique ID: {sticker_unique_id}")
    existing_sticker = StickerManager.sticker_exists(user_id, sticker_unique_id)
    print(f"Existing sticker result: {existing_sticker}")

    if existing_sticker:
        # This sticker already exists, offer to edit it
        bot.set_sticker_state(user_id, StickerStates.EDITING_EXISTING_STICKER)

        # Show the existing details and ask if they want to edit
        existing_tags = existing_sticker.get('tags', [])
        current_tags_str = ', '.join(existing_tags) if existing_tags else 'No tags'
        current_emoji = existing_sticker.get('emoji', 'No emoji')

        await message.reply_sticker(sticker_id)
        await message.reply_text(
            f"This sticker already exists in your collection!\n\n"
            f"Current details:\n"
            f"Tags: {current_tags_str}\n"
            f"Emoji: {current_emoji}\n\n"
            f"Would you like to edit this sticker?",
            reply_markup=get_edit_existing_sticker_keyboard()
        )
    else:
        # New sticker, continue with regular flow
        bot.set_sticker_state(user_id, StickerStates.WAITING_FOR_TAG)
        await message.reply_text(
            "You sent a new sticker!\nSend me the tag for this sticker or use the buttons below.",
            reply_markup=get_tag_keyboard()
        )


@StickerBot.on_message(filters.regex(r'^(?!/)') & filters.text)
async def set_tag(bot: StickerBot, message: Message):
    user_id = message.from_user.id

    # Handle keyboard button presses
    if message.text == "Skip Tags":
        bot.set_tag(user_id, "")  # Set empty tag instead of None
        bot.set_sticker_state(user_id, StickerStates.SELECTING_EMOJI)
        await message.reply_text(
            "Tags skipped! Now select an emoji for your sticker:",
            reply_markup=get_common_emojis_keyboard()
        )
        return

    if message.text == "Cancel":
        bot.set_sticker_state(user_id, StickerStates.NOTHING)
        await message.reply_text("Process cancelled.", reply_markup=get_main_keyboard())
        return

    if message.text == "Help with Tags":
        await message.reply_text(
            "You can add multiple tags by separating them with commas.\n"
            "Example: 'funny, meme, laugh' or 'cat, pet, cute'\n\n"
            "Send your tags now (separated by commas):"
        )
        return

    if bot.get_sticker_state(user_id) is StickerStates.WAITING_FOR_TAG:
        from app.helpers.string_parsers import parse_tags, validate_tag

        # Parse tags from user input (could be multiple tags)
        tags = parse_tags(message.text)

        if tags and all(validate_tag(tag) for tag in tags):  # Validate all tags
            bot.set_sticker_state(user_id, StickerStates.SELECTING_EMOJI)
            bot.set_tag(user_id, message.text)  # Store the original input
            await message.reply_text(
                f"Tags '{', '.join(tags)}' received! Now select an emoji for your sticker:",
                reply_markup=get_common_emojis_keyboard()
            )
        else:
            await message.reply_text(
                "Please send valid tags (single words separated by commas or spaces) or use the buttons below:",
                reply_markup=get_tag_keyboard()
            )

    elif bot.get_sticker_state(user_id) is StickerStates.WAITING_FOR_EMOJI:
        if is_emoji(message.text):
            bot.set_emoji(user_id, message.text)
            bot.set_sticker_state(user_id, StickerStates.CONFIRMING_STICKER)
            tag = bot.get_tag(user_id)
            sticker_id = bot.get_sticker_id(user_id)

            # Debug: Check values before sending confirmation
            current_state = bot.get_sticker_state(user_id)
            emoji_debug = bot.get_emoji(user_id)
            print(f"Before confirmation (WAITING_FOR_EMOJI) - User: {user_id}, State: {current_state}, StickerID: {sticker_id}, Tag: {tag}, Emoji: {emoji_debug}")

            # Send the sticker with confirmation options
            await message.reply_sticker(sticker_id)
            # Parse tags to show them properly
            from app.helpers.string_parsers import parse_tags
            tags_list = parse_tags(tag) if tag else []
            tags_display = ', '.join(tags_list) if tags_list else 'No tag'
            await message.reply_text(
                f"Sticker details:\nTags: {tags_display}\nEmoji: {message.text}\n\nConfirm to save:",
                reply_markup=get_confirmation_keyboard()
            )
        else:
            await message.reply_text(
                "Please send a valid emoji or use the buttons below:",
                reply_markup=get_emoji_keyboard()
            )

    elif bot.get_sticker_state(user_id) is StickerStates.SELECTING_EMOJI:
        if is_emoji(message.text):
            bot.set_emoji(user_id, message.text)
            bot.set_sticker_state(user_id, StickerStates.CONFIRMING_STICKER)
            tag = bot.get_tag(user_id)
            sticker_id = bot.get_sticker_id(user_id)

            # Debug: Check values before sending confirmation
            current_state = bot.get_sticker_state(user_id)
            emoji_debug = bot.get_emoji(user_id)
            print(f"Before confirmation (SELECTING_EMOJI) - User: {user_id}, State: {current_state}, StickerID: {sticker_id}, Tag: {tag}, Emoji: {emoji_debug}")

            # Send the sticker with confirmation options
            await message.reply_sticker(sticker_id)
            # Parse tags to show them properly
            from app.helpers.string_parsers import parse_tags
            tags_list = parse_tags(tag) if tag else []
            tags_display = ', '.join(tags_list) if tags_list else 'No tag'
            await message.reply_text(
                f"Sticker details:\nTags: {tags_display}\nEmoji: {message.text}\n\nConfirm to save:",
                reply_markup=get_confirmation_keyboard()
            )
        else:
            await message.reply_text(
                "Please send a valid emoji or use the buttons below:",
                reply_markup=get_emoji_keyboard()
            )

    elif bot.get_sticker_state(user_id) is StickerStates.EDITING_EXISTING_STICKER:
        # Handle editing for existing stickers - this case shouldn't happen since
        # we don't set the state to EDITING_EXISTING_STICKER for text input
        # The actual editing is handled by the callback query handlers
        pass


@StickerBot.on_callback_query(filters.regex(r'^emoji_'))
async def handle_emoji_selection(bot: StickerBot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    selected_emoji = callback_query.data.replace('emoji_', '')

    if bot.get_sticker_state(user_id) in [StickerStates.SELECTING_EMOJI, StickerStates.WAITING_FOR_EMOJI]:
        bot.set_emoji(user_id, selected_emoji)
        bot.set_sticker_state(user_id, StickerStates.CONFIRMING_STICKER)

        tag = bot.get_tag(user_id)
        sticker_id = bot.get_sticker_id(user_id)

        # Debug: Check values before sending confirmation
        current_state = bot.get_sticker_state(user_id)
        emoji_debug = bot.get_emoji(user_id)
        print(f"Before confirmation (callback emoji selection) - User: {user_id}, State: {current_state}, StickerID: {sticker_id}, Tag: {tag}, Emoji: {emoji_debug}")

        # Send the sticker with confirmation options
        await callback_query.message.reply_sticker(sticker_id)
        await callback_query.message.reply_text(
            f"Sticker details:\nTag: {tag if tag else 'No tag'}\nEmoji: {selected_emoji}\n\nConfirm to save:",
            reply_markup=get_confirmation_keyboard()
        )

        await callback_query.answer(f"Selected emoji: {selected_emoji}")
    elif bot.get_sticker_state(user_id) == StickerStates.EDITING_EXISTING_STICKER:
        # Update emoji of existing sticker directly
        sticker_unique_id = bot.get_sticker_unique_id(user_id)  # Use unique_id for editing
        current_tag = bot.get_tag(user_id)

        # Convert single tag string to a list
        current_tags_list = [current_tag] if current_tag else []

        # Update the existing sticker in the database
        result = StickerManager.update_sticker(user_id, sticker_unique_id, current_tags_list, selected_emoji)

        if result and result.modified_count > 0:
            await callback_query.message.reply_text(
                f"Sticker updated successfully!\nNew emoji: {selected_emoji}",
                reply_markup=get_main_keyboard()
            )
            await callback_query.answer("Emoji updated!")
        else:
            await callback_query.message.reply_text(
                "Failed to update sticker emoji.",
                reply_markup=get_main_keyboard()
            )
            await callback_query.answer("Update failed")

        bot.set_sticker_state(user_id, StickerStates.NOTHING)
    else:
        await callback_query.answer("Invalid selection. Please send a sticker first.")


@StickerBot.on_callback_query(filters.regex(r'^cancel_emoji'))
async def handle_cancel_emoji_selection(bot: StickerBot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    bot.set_sticker_state(user_id, StickerStates.NOTHING)
    await callback_query.message.reply_text("Emoji selection cancelled.", reply_markup=get_main_keyboard())
    await callback_query.answer("Cancelled")


@StickerBot.on_callback_query(filters.regex(r'^edit_existing_'))
async def handle_edit_existing_sticker(bot: StickerBot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    action = callback_query.data

    # Get the existing sticker to preserve data
    sticker_unique_id = bot.get_sticker_unique_id(user_id)
    existing_sticker = StickerManager.sticker_exists(user_id, sticker_unique_id)

    if not existing_sticker:
        await callback_query.message.reply_text("Error: Sticker not found.")
        await callback_query.answer("Error")
        return

    if action == "edit_existing_tag":
        # Set tag to existing value and go to tag editing state
        # For backward compatibility, convert tags list to string representation
        existing_tags = existing_sticker.get('tags', [])
        existing_tags_str = ', '.join(existing_tags) if existing_tags else ''

        # Store the sticker unique ID so we can update the right sticker later
        sticker_unique_id = existing_sticker.get('sticker_unique_id')
        if sticker_unique_id:
            bot.set_sticker_unique_id(user_id, sticker_unique_id)

        bot.set_tag(user_id, existing_tags_str)
        bot.set_emoji(user_id, existing_sticker.get('emoji', ''))
        bot.set_sticker_state(user_id, StickerStates.WAITING_FOR_TAG)
        await callback_query.message.reply_text(
            f"Current tags: '{existing_tags_str if existing_tags_str else 'No tags'}'\nSend me the new tags (separated by commas) or use buttons below:",
            reply_markup=get_tag_keyboard()
        )
        await callback_query.answer("Editing tag")

    elif action == "edit_existing_emoji":
        # Set emoji to existing value and go to emoji selection state
        # For backward compatibility, convert tags list to string representation
        existing_tags = existing_sticker.get('tags', [])
        existing_tags_str = ', '.join(existing_tags) if existing_tags else ''

        # Store the sticker unique ID so we can update the right sticker later
        sticker_unique_id = existing_sticker.get('sticker_unique_id')
        if sticker_unique_id:
            bot.set_sticker_unique_id(user_id, sticker_unique_id)

        bot.set_tag(user_id, existing_tags_str)
        bot.set_emoji(user_id, existing_sticker.get('emoji', ''))
        bot.set_sticker_state(user_id, StickerStates.SELECTING_EMOJI)
        await callback_query.message.reply_text(
            f"Current emoji: '{existing_sticker.get('emoji', 'No emoji')}'\nSelect a new emoji or send one:",
            reply_markup=get_common_emojis_keyboard()
        )
        await callback_query.answer("Editing emoji")

    elif action == "edit_both_existing":
        # Start with editing tag first
        # For backward compatibility, convert tags list to string representation
        existing_tags = existing_sticker.get('tags', [])
        existing_tags_str = ', '.join(existing_tags) if existing_tags else ''

        # Store the sticker unique ID so we can update the right sticker later
        sticker_unique_id = existing_sticker.get('sticker_unique_id')
        if sticker_unique_id:
            bot.set_sticker_unique_id(user_id, sticker_unique_id)

        bot.set_tag(user_id, existing_tags_str)
        bot.set_emoji(user_id, existing_sticker.get('emoji', ''))
        bot.set_sticker_state(user_id, StickerStates.WAITING_FOR_TAG)
        await callback_query.message.reply_text(
            f"Current tags: '{existing_tags_str if existing_tags_str else 'No tags'}'\nSend me the new tags (separated by commas) or use buttons below:",
            reply_markup=get_tag_keyboard()
        )
        await callback_query.answer("Editing both tag and emoji")

    elif action == "cancel_edit_existing":
        bot.set_sticker_state(user_id, StickerStates.NOTHING)
        await callback_query.message.reply_text("Edit cancelled.", reply_markup=get_main_keyboard())
        await callback_query.answer("Cancelled")


@StickerBot.on_callback_query(filters.regex(r'^confirm_update'))
async def handle_confirm_update_sticker(bot: StickerBot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    sticker_unique_id = bot.get_sticker_unique_id(user_id)  # Use unique_id for update
    new_tag = bot.get_tag(user_id)
    new_emoji = bot.get_emoji(user_id)

    # Convert single tag string to a list
    new_tags_list = [new_tag] if new_tag else []

    # Update the existing sticker
    result = StickerManager.update_sticker(user_id, sticker_unique_id, new_tags_list, new_emoji)

    if result and result.modified_count > 0:
        await callback_query.message.reply_text(
            f"Sticker updated successfully!\nNew tag: {new_tag if new_tag else 'No tag'}\nNew emoji: {new_emoji if new_emoji else 'No emoji'}",
            reply_markup=get_main_keyboard()
        )
        await callback_query.answer("Sticker updated!")
    else:
        await callback_query.message.reply_text(
            "Failed to update sticker.",
            reply_markup=get_main_keyboard()
        )
        await callback_query.answer("Update failed")

    bot.set_sticker_state(user_id, StickerStates.NOTHING)


@StickerBot.on_callback_query(filters.regex(r'^(confirm_save|cancel_save|edit_tag|edit_emoji)'))
async def handle_confirmation(bot: StickerBot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    action = callback_query.data

    if action == "confirm_save":
        # Debug: Check all values in the user's state
        sticker_id = bot.get_sticker_id(user_id)
        tag = bot.get_tag(user_id)
        emoji = bot.get_emoji(user_id)
        current_state = bot.get_sticker_state(user_id)

        print(f"Confirm save - User: {user_id}, State: {current_state}, StickerID: {sticker_id}, Tag: {tag}, Emoji: {emoji}")

        # Validate that we have all required values before saving
        if not sticker_id:
            await callback_query.message.reply_text("Error: No sticker was provided. Please start over.", reply_markup=get_main_keyboard())
            bot.set_sticker_state(user_id, StickerStates.NOTHING)
            await callback_query.answer("Error occurred")
            return
        # Pass the user_id to ensure correct context
        await handle_sticker_saving_with_user_id(bot, callback_query.message, user_id)
    elif action == "cancel_save":
        bot.set_sticker_state(user_id, StickerStates.NOTHING)
        await callback_query.message.reply_text("Sticker saving cancelled.", reply_markup=get_main_keyboard())
        await callback_query.answer("Cancelled")
    elif action == "edit_tag":
        bot.set_sticker_state(user_id, StickerStates.WAITING_FOR_TAG)
        await callback_query.message.reply_text(
            "Send me the new tag for this sticker or use the buttons below:",
            reply_markup=get_tag_keyboard()
        )
        await callback_query.answer("Edit tag")
    elif action == "edit_emoji":
        bot.set_sticker_state(user_id, StickerStates.SELECTING_EMOJI)
        await callback_query.message.reply_text(
            "Select a new emoji for this sticker:",
            reply_markup=get_common_emojis_keyboard()
        )
        await callback_query.answer("Edit emoji")


async def handle_sticker_saving_with_user_id(bot: StickerBot, message: Message, user_id: int):
    sticker_id = bot.get_sticker_id(user_id)
    sticker_unique_id = bot.get_sticker_unique_id(user_id)
    tag_string = bot.get_tag(user_id)
    emoji_string = bot.get_emoji(user_id)

    # Debug: Print state values when saving
    current_state = bot.get_sticker_state(user_id)
    print(f"Handle sticker saving - User: {user_id}, State: {current_state}, StickerID: {sticker_id}, StickerUniqueID: {sticker_unique_id}, Tag: {tag_string}, Emoji: {emoji_string}")

    # Validate that we have the required values before saving
    if not sticker_id:
        await message.reply_text("Error: No sticker ID found. Please try again.", reply_markup=get_main_keyboard())
        bot.set_sticker_state(user_id, StickerStates.NOTHING)
        return

    # Check if we have all required data
    if emoji_string is None:
        await message.reply_text("Error: No emoji was provided. Please try again.", reply_markup=get_main_keyboard())
        bot.set_sticker_state(user_id, StickerStates.NOTHING)
        return

    # Parse multiple tags from the tag string
    from app.helpers.string_parsers import parse_tags
    tags_list = parse_tags(tag_string) if tag_string else []

    # Check if this is an existing sticker being updated (use unique_id for this check)
    existing_sticker = StickerManager.sticker_exists(user_id, sticker_unique_id)

    try:
        if existing_sticker:
            # This is an existing sticker, update it
            result = StickerManager.update_sticker(user_id, sticker_unique_id, tags_list, emoji_string)
            if result and result.modified_count > 0:
                print(f"Sticker updated successfully")
                await message.reply_text("Sticker updated successfully!", reply_markup=get_main_keyboard())
            else:
                await message.reply_text("Sticker update failed!", reply_markup=get_main_keyboard())
        else:
            # This is a new sticker, insert it
            response = StickerManager.insert_sticker(user_id, sticker_id, sticker_unique_id, tags_list, emoji_string)
            if response.inserted_id:
                print(f"Sticker saved with ID: {response.inserted_id}")
                await message.reply_text("Sticker saved successfully!", reply_markup=get_main_keyboard())
            else:
                await message.reply_text("Sticker saving failed!", reply_markup=get_main_keyboard())
    except ValueError as e:
        await message.reply_text(f"Error saving sticker: {str(e)}", reply_markup=get_main_keyboard())
        print(f"ValueError during sticker saving: {e}")

    bot.set_sticker_state(user_id, StickerStates.NOTHING)

# Original function for any other calls
async def handle_sticker_saving(bot: StickerBot, message: Message):
    # Use the message's user id - this is kept for other potential calls
    user_id = message.from_user.id
    await handle_sticker_saving_with_user_id(bot, message, user_id)


@StickerBot.on_message(filters.regex(r'^Recent Emojis$'))
async def show_recent_emojis(bot: StickerBot, message: Message):
    user_id = message.from_user.id

    if bot.get_sticker_state(user_id) == StickerStates.SELECTING_EMOJI:
        # In a real app, we could fetch recent emojis used by the user
        await message.reply_text(
            "Select an emoji for your sticker:",
            reply_markup=get_common_emojis_keyboard()
        )
    else:
        await message.reply_text("Please send a sticker first to begin the saving process.")


@StickerBot.on_message(filters.regex(r'^Skip Emoji$'))
async def skip_emoji(bot: StickerBot, message: Message):
    user_id = message.from_user.id

    if bot.get_sticker_state(user_id) in [StickerStates.SELECTING_EMOJI, StickerStates.WAITING_FOR_EMOJI]:
        bot.set_emoji(user_id, "")  # Set empty emoji instead of None
        bot.set_sticker_state(user_id, StickerStates.CONFIRMING_STICKER)
        tag = bot.get_tag(user_id)
        sticker_id = bot.get_sticker_id(user_id)

        # Send the sticker with confirmation options
        await message.reply_sticker(sticker_id)
        await message.reply_text(
            f"Sticker details:\nTag: {tag if tag else 'No tag'}\nEmoji: No emoji\n\nConfirm to save:",
            reply_markup=get_confirmation_keyboard()
        )
