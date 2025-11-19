# Sticker Helper Bot

## Project Overview
This is a Telegram bot designed to help users manage and organize stickers. The bot allows users to save stickers with associated tags and emojis to a MongoDB database, and then search and use these stickers through inline queries. It's built using the Pyrogram library for Telegram API interaction. The bot supports multiple users simultaneously, each with their own sticker collection.

## Architecture
- **Main Bot Class**: `StickerBot` extends Pyrogram's `Client` class and manages the bot state and interactions
- **Plugins System**: Uses Pyrogram's plugin system with separate files for different functionalities
- **Helpers**: Contains utility functions for parsing strings, managing sticker state, and database operations
- **Database**: Uses MongoDB as the backend database to store sticker information with proper user isolation
- **Database Layer**: Abstraction layer with `StickerDB` and `UserDB` classes for database operations

## Key Features
1. **Multi-User Support**: Each user has their own independent sticker collection and workflow state
2. **Sticker Saving**: Users can send stickers to the bot, then provide tags and emojis to save the sticker to the database
3. **Interactive UI**: Uses reply keyboards and inline keyboards for easier sticker tagging and emoji selection
4. **Duplicate Detection**: Uses `file_unique_id` to detect when the same sticker (even with different `file_id`) is sent again and offers to edit existing sticker
5. **Multiple Tags**: Supports multiple tags per sticker for better searchability
6. **State Management**: Tracks each user's state (waiting for tag, waiting for emoji, etc.) to guide user interactions
7. **Inline Search**: Allows users to search their own stickers by tags or emojis directly from the chat
8. **Edit Functionality**: Users can edit existing stickers' tags and emojis
9. **Logging**: Comprehensive logging with file rotation for debugging and monitoring

## File Structure
```
stickerbot/
├── __init__.py         # Initializes logging, config and globals
├── __main__.py         # Main entry point
├── stickerbot.py       # Main bot class with state management
├── database/           # Database layer
│   ├── __init__.py     # Database connection function
│   ├── sticker_db.py   # Sticker database operations
│   └── user_db.py      # User database operations
├── helpers/            # Utility functions
│   ├── sticker_manager.py      # Database operations for stickers
│   ├── sticker_state_enum.py   # State enum for bot workflow
│   ├── string_parsers.py       # String validation and tag parsing utilities
│   └── keyboard_utils.py       # Keyboard creation utilities
└── plugins/            # Bot command handlers
    ├── inline.py       # Handles inline sticker search
    ├── save_sticker.py # Handles sticker saving workflow
    └── start.py        # Handles /start command
```

## Dependencies
- `pyrogram` - Telegram client library
- `tgcrypto` - Cryptographic library for Pyrogram
- `pymongo` - MongoDB client for database operations
- `emoji` - Emoji validation and processing

## Configuration
The bot requires a `config.ini` file with the following structure:
```
[pyrogram]
api_id = YOUR_API_ID
api_hash = YOUR_API_HASH
bot_token = YOUR_BOT_TOKEN
admin = ADMIN_USER_ID

[mongodb]
uri = YOUR_MONGODB_URI
database_name = YOUR_DATABASE_NAME
```

## Building and Running
1. Install dependencies: `pip install -r requirements.txt`
2. Create a `config.ini` file with the appropriate configuration (see above)
3. Run the bot: `python -m stickerbot` or `python stickerbot/__main__.py`

## Bot Workflow
1. User sends a sticker to the bot
2. If the sticker already exists (based on file_unique_id), bot offers to edit it
3. If new, bot enters `WAITING_FOR_TAG` state and prompts for tags (multiple tags supported, separated by commas)
4. User sends tags (or uses keyboard buttons for skip/help/cancel options)
5. Bot enters `SELECTING_EMOJI` state and provides emoji selection options
6. User can select emoji from inline keyboard or send an emoji directly
7. Bot shows confirmation with sticker and details, asking to confirm before saving
8. User confirms, edits, or cancels the operation
9. For searching, user uses inline mode (`@botname`) to find and send their saved stickers
10. User can edit existing stickers by sending them again

## Interactive Features
- **Reply keyboards**: For tag entry with options to skip tags, get help, or cancel
- **Inline keyboards**: For emoji selection with common emojis
- **Confirmation flow**: For final review before saving stickers
- **Edit options**: For modifying tags/emojis of existing stickers
- **Multiple tags**: Support for entering multiple tags separated by commas

## Development Conventions
- Follows Pyrogram's plugin architecture pattern
- Uses type hints for better code maintainability
- Implements user-specific state management for multi-user support
- Centralized logging with file rotation for debugging
- Database operations are abstracted through the StickerManager and UserDB classes
- Proper error handling and validation at each layer

## Security
- Each user's stickers are properly isolated by user_id
- Access to inline search only shows user's own stickers
- Proper validation of all inputs before database operations