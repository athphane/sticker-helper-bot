from app.database.sticker_db import StickerDB

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
            print(f"Error inserting sticker: {e}")
            raise e

    @staticmethod
    def all_stickers_like(search: str, user_id: int, limit: int = 10):
        results = _db.find_stickers_like(search, user_id, limit)
        return {"data": results}

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
    def update_sticker(user_id: int, sticker_unique_id: str, new_tags: list, new_emoji: str):
        """Update an existing sticker with new tags and emoji"""
        # Convert single tag to list if needed
        if isinstance(new_tags, str):
            new_tags = [new_tags] if new_tags else []
        try:
            return _db.update_sticker(user_id, sticker_unique_id, new_tags, new_emoji)
        except ValueError as e:
            print(f"Error updating sticker: {e}")
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
            print(f"Error adding tags to sticker: {e}")
            raise e
