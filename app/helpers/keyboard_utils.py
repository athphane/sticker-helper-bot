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
        [KeyboardButton("Random Sticker"), KeyboardButton("My Collection")],
        [KeyboardButton("/start"), KeyboardButton("/help"), KeyboardButton("/clear")]
    ], resize_keyboard=True)

def get_browse_keyboard():
    """Return an inline keyboard for browsing a user's sticker collection"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("◀ Prev", callback_data="browse_prev"),
            InlineKeyboardButton("Next ▶", callback_data="browse_next")
        ],
        [
            InlineKeyboardButton("Delete", callback_data="browse_delete"),
            InlineKeyboardButton("Edit", callback_data="browse_edit")
        ],
        [
            InlineKeyboardButton("Close", callback_data="browse_close")
        ]
    ])

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
        ],
        [
            InlineKeyboardButton("Delete Sticker", callback_data="delete_existing")
        ]
    ])

def get_delete_confirmation_keyboard():
    """Return an inline keyboard to confirm deleting a sticker"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Confirm Delete", callback_data="confirm_delete"),
            InlineKeyboardButton("Cancel", callback_data="cancel_delete")
        ]
    ])

def get_recent_emojis_keyboard(emojis):
    """Return an inline keyboard built from the user's recently used emojis"""
    rows = [emojis[i:i + 3] for i in range(0, len(emojis), 3)]
    keyboard = [[InlineKeyboardButton(e, callback_data=f"emoji_{e}") for e in row] for row in rows]
    keyboard.append([InlineKeyboardButton("Cancel", callback_data="cancel_emoji")])
    return InlineKeyboardMarkup(keyboard)

def get_multiple_tag_keyboard():
    """Return a reply keyboard for multiple tag entry"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("Add More Tags")],  # For adding additional tags
        [KeyboardButton("Skip Tags")],  # Option to skip adding tags
        [KeyboardButton("Cancel")]  # Option to cancel the process
    ], resize_keyboard=True, one_time_keyboard=True)