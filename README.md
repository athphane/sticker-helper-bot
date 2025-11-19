# Sticker Helper Bot

A comprehensive Telegram bot that helps users save and organize stickers with custom tags and emojis for easy retrieval. The bot supports multiple users, each with their own sticker collection, and provides an interactive interface for managing stickers.

## Features

### Multi-User Support
- Each user has their own independent sticker collection
- User-specific workflow states for better experience
- Proper user isolation to ensure privacy between users

### Interactive Sticker Saving
- User-friendly keyboard interface for tagging and categorizing stickers
- Multiple tag support (tags separated by commas)
- Emoji selection interface with common emoji suggestions
- Confirmation flow for sticker saving with edit options

### Advanced Sticker Management
- Duplicate detection using file_unique_id for accurate identification
- Edit existing stickers functionality
- Support for multiple tags per sticker for enhanced searchability
- Inline search showing user-specific stickers only

### Database Layer
- Migrated from Supabase to MongoDB for improved scalability
- Database abstraction layer with StickerDB and UserDB classes
- Proper error handling and validation throughout the application

### User Experience
- Reply keyboards and inline keyboards for easier interactions
- Multiple tag support with comma-separated entry
- Emoji picker for quick emoji assignment
- Review and confirmation before saving stickers

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd sticker-helper-bot
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `config.ini` file in the project root with the following structure:

```ini
[pyrogram]
api_id = YOUR_API_ID
api_hash = YOUR_API_HASH
bot_token = YOUR_BOT_TOKEN
admin = ADMIN_USER_ID

[mongodb]
uri = YOUR_MONGODB_URI
database_name = stickerbot
```

### Getting Required Values

- **API ID & Hash**: Create an app at [my.telegram.org](https://my.telegram.org) to get your API credentials
- **Bot Token**: Create a bot with [@BotFather](https://t.me/BotFather) on Telegram
- **Admin User ID**: Your Telegram user ID (you can find it using [@userinfobot](https://t.me/userinfobot))
- **MongoDB URI**: Create a MongoDB Atlas account or use a local instance

## Usage

1. Start the bot:
   ```bash
   python -m stickerbot
   ```

2. **Adding Stickers**:
   - Send the bot a sticker
   - If it's new, you'll be prompted to add tags (multiple tags supported, separated by commas)
   - Select an emoji using the keyboard or send one directly
   - Review the details and confirm to save

3. **Editing Existing Stickers**:
   - Send the same sticker again (even if sent from different context)
   - The bot will detect it using file_unique_id and offer to edit the existing sticker
   - Choose to edit tags, emoji, or both

4. **Searching Stickers**:
   - In any chat, type `@your_bot_username` followed by a search term
   - The bot will show matching stickers from your collection

## Commands

- `/start` - Get started and see your sticker count
- `/clear` - Reset the current sticker saving process

## How It Works

The bot uses Telegram's unique file identifiers (file_unique_id) to detect duplicate stickers, ensuring that even if the same sticker is sent from different sources, it's recognized as the same sticker. Each sticker can have multiple tags for better organization and searchability.

All data is stored in MongoDB, with proper user isolation to ensure privacy between users. The system features a comprehensive database abstraction layer for better maintainability and scalability.

## Architecture

### File Structure
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

### Plugin System
- Separate handlers for different bot functionalities
- Database abstraction layer for operations
- Helper functions for parsing and processing
- State management for user-specific contexts

## Development

The project uses Pyrogram's plugin architecture pattern with type hints for better code maintainability. Database operations are abstracted through the StickerManager and UserDB classes. Proper error handling and validation is implemented at each layer.

### Dependencies
- `pyrogram` - Telegram client library
- `tgcrypto` - Cryptographic library for Pyrogram
- `pymongo` - MongoDB client for database operations
- `emoji` - Emoji validation and processing

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please open an issue in the repository.