class StickerStates:
    NOTHING = 0
    WAITING_FOR_EMOJI = 1
    WAITING_FOR_TAG = 2
    SAVING_STICKER = 3
    SELECTING_EMOJI = 4  # New state for emoji keyboard selection
    CONFIRMING_STICKER = 5  # New state for confirming before saving
    EDITING_EXISTING_STICKER = 6  # New state for editing existing stickers

