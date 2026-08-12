import logging

from app.database.sticker_db import StickerDB

LOGS = logging.getLogger(__name__)

# One DB accessor reused process-wide (its backing client is a shared singleton).
_db = StickerDB()


class StickerManager:
    @staticmethod
    def insert_sticker(user_id: int, sticker_id: str, sticker_unique_id: str, tags: list, emoji: str):
        # Convert single tag to list if needed
        if isinstance(tags, str):
            tags = [tags] if tags else []
        try:
            return _db.insert_sticker(user_id, sticker_id, sticker_unique_id, tags, emoji)
        except ValueError as e:
            LOGS.error(f"Error inserting sticker: {e}")
            raise e

    @staticmethod
    def all_stickers_like(search: str, user_id: int, limit: int = 50, offset: int = 0):
        return _db.find_stickers_like(search, user_id, limit, offset)

    @staticmethod
    def find_sticker_by_user(sticker_unique_id: str, user_id: int):
        return _db.find_sticker(sticker_unique_id, user_id)

    @staticmethod
    def find_stickers_by_user(user_id: int):
        return _db.find_stickers_by_user(user_id)

    @staticmethod
    def get_user_sticker_count(user_id: int):
        return _db.get_user_sticker_count(user_id)

    @staticmethod
    def sticker_exists(user_id: int, sticker_unique_id: str):
        """Check if a sticker with given unique ID already exists for the user"""
        return _db.sticker_exists(user_id, sticker_unique_id)

    @staticmethod
    def delete_sticker(user_id: int, sticker_unique_id: str):
        """Delete a sticker by its unique ID for a given user"""
        try:
            return _db.delete_sticker(user_id, sticker_unique_id)
        except ValueError as e:
            LOGS.error(f"Error deleting sticker: {e}")
            raise e

    @staticmethod
    def update_sticker(user_id: int, sticker_unique_id: str, new_tags: list, new_emoji: str):
        """Update an existing sticker with new tags and emoji"""
        # Convert single tag to list if needed
        if isinstance(new_tags, str):
            new_tags = [new_tags] if new_tags else []
        try:
            return _db.update_sticker(user_id, sticker_unique_id, new_tags, new_emoji)
        except ValueError as e:
            LOGS.error(f"Error updating sticker: {e}")
            raise e

    @staticmethod
    def add_tags_to_sticker(user_id: int, sticker_unique_id: str, new_tags: list):
        """Add new tags to an existing sticker"""
        # Convert single tag to list if needed
        if isinstance(new_tags, str):
            new_tags = [new_tags] if new_tags else []
        try:
            return _db.add_tags_to_sticker(user_id, sticker_unique_id, new_tags)
        except ValueError as e:
            LOGS.error(f"Error adding tags to sticker: {e}")
            raise e

    @staticmethod
    def get_recent_emojis(user_id: int, limit: int = 9):
        """Return the most recently used emojis for a user"""
        return _db.get_recent_emojis(user_id, limit)

    @staticmethod
    def get_random_sticker(user_id: int):
        """Return a random sticker for a user, or None if the collection is empty"""
        return _db.get_random_sticker(user_id)

    @staticmethod
    def increment_sticker_use(user_id: int, sticker_unique_id: str):
        """Increment the use count of a sticker when it is sent via inline mode"""
        return _db.increment_sticker_use(user_id, sticker_unique_id)

    @staticmethod
    def get_stats(user_id: int, limit: int = 5):
        """Aggregate usage metrics for a user: sticker/tag/emoji popularity"""
        return _db.get_stats(user_id, limit)
