from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_tag_keyboard():
    """Return a reply keyboard for tag entry"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("Skip Tags")],  # Option to skip adding tags
        [KeyboardButton("Help with Tags")],  # Option to get help about multiple tags
        [KeyboardButton("Cancel")]  # Option to cancel the process
    ], resize_keyboard=True, one_time_keyboard=True)

def get_emoji_keyboard():
    """Return a reply keyboard for emoji entry"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("Recent Emojis")],  # Commonly used emojis
        [KeyboardButton("Skip Emoji")],  # Option to skip adding an emoji
        [KeyboardButton("Cancel")]  # Option to cancel the process
    ], resize_keyboard=True, one_time_keyboard=True)

def get_common_emojis_keyboard():
    """Return an inline keyboard with common emojis for selection"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("😀", callback_data="emoji_😀"),
            InlineKeyboardButton("😍", callback_data="emoji_😍"),
            InlineKeyboardButton("😂", callback_data="emoji_😂")
        ],
        [
            InlineKeyboardButton("❤️", callback_data="emoji_❤️"),
            InlineKeyboardButton("👍", callback_data="emoji_👍"),
            InlineKeyboardButton("👌", callback_data="emoji_👌")
        ],
        [
            InlineKeyboardButton("✅", callback_data="emoji_✅"),
            InlineKeyboardButton("❌", callback_data="emoji_❌"),
            InlineKeyboardButton("Cancel", callback_data="cancel_emoji")
        ]
    ])

def get_confirmation_keyboard():
    """Return an inline keyboard for sticker confirmation"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Confirm", callback_data="confirm_save"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_save")
        ],
        [
            InlineKeyboardButton("Edit Tag", callback_data="edit_tag"),
            InlineKeyboardButton("Edit Emoji", callback_data="edit_emoji")
        ]
    ])

def get_main_keyboard():
    """Return the main keyboard"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("/start"), KeyboardButton("/help")],
        [KeyboardButton("/clear")]
    ], resize_keyboard=True)

def get_edit_existing_sticker_keyboard():
    """Return an inline keyboard for editing existing stickers"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Edit Tag", callback_data="edit_existing_tag"),
            InlineKeyboardButton("Edit Emoji", callback_data="edit_existing_emoji")
        ],
        [
            InlineKeyboardButton("Edit Both", callback_data="edit_both_existing"),
            InlineKeyboardButton("Cancel", callback_data="cancel_edit_existing")
        ]
    ])

def get_multiple_tag_keyboard():
    """Return a reply keyboard for multiple tag entry"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("Add More Tags")],  # For adding additional tags
        [KeyboardButton("Skip Tags")],  # Option to skip adding tags
        [KeyboardButton("Cancel")]  # Option to cancel the process
    ], resize_keyboard=True, one_time_keyboard=True)