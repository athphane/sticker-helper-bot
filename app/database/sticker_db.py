import logging
from datetime import datetime

from app.database import database

LOGS = logging.getLogger(__name__)


class StickerDB:
    def __init__(self):
        # Get the database from the database() function
        db_instance = database()
        # The database() function now returns the specific database, not the client
        self.stickers = db_instance['stickers']

    def all_stickers(self):
        stickers = self.stickers.find()
        return stickers

    def find_sticker(self, sticker_unique_id: str, user_id: int):
        query = {
            "sticker_unique_id": sticker_unique_id,
            "user_id": user_id
        }
        record = self.stickers.find_one(query)
        return record

    def find_stickers_by_user(self, user_id: int):
        query = {"user_id": user_id}
        results = list(self.stickers.find(query))
        return results

    def find_stickers_like(self, search: str, user_id: int, limit: int = 50, offset: int = 0):
        if search:
            # Search for stickers where any tag in the tags array contains the search term (case-insensitive) or emoji matches exactly
            # Only return stickers for the specific user
            # Use $elemMatch with $regex to find documents where at least one array element matches the regex
            query = {
                "user_id": user_id,
                "$or": [
                    {
                        "tags": {
                            "$elemMatch": {
                                "$regex": search,
                                "$options": "i"
                            }
                        }
                    },
                    {"emoji": {"$regex": f"^{search}$", "$options": "i"}}  # Exact emoji match
                ]
            }

            results = list(self.stickers.find(query).skip(offset).limit(limit))
        else:
            # Return stickers for the specific user if no search term
            query = {"user_id": user_id}
            results = list(self.stickers.find(query).skip(offset).limit(limit))

        return results

    def insert_sticker(self, user_id: int, sticker_id: str, sticker_unique_id: str, tags: list, emoji: str):
        # Validate required fields
        if not sticker_id or not sticker_unique_id:
            raise ValueError("sticker_id and sticker_unique_id cannot be empty or None")

        # Convert a single tag string to a list if needed
        if isinstance(tags, str):
            tags = [tags] if tags else []

        sticker_doc = {
            "user_id": user_id,
            "sticker_id": sticker_id,        # The actual file ID for sending
            "sticker_unique_id": sticker_unique_id,  # The unique ID for duplicate detection
            "tags": tags,  # Now storing as a list
            "emoji": emoji,
            "use_count": 0,  # Times this sticker was sent via inline mode
            "created_at": datetime.now(),
        }
        result = self.stickers.insert_one(sticker_doc)
        return result

    def delete_sticker(self, user_id: int, sticker_unique_id: str):
        result = self.stickers.delete_one({"sticker_unique_id": sticker_unique_id, "user_id": user_id})
        return result.deleted_count

    def get_user_sticker_count(self, user_id: int):
        count = self.stickers.count_documents({"user_id": user_id})
        return count

    def sticker_exists(self, user_id: int, sticker_unique_id: str):
        """Check if a sticker with given unique ID already exists for the user"""
        query = {
            "user_id": user_id,
            "sticker_unique_id": sticker_unique_id
        }
        LOGS.debug(f"Database query for existing sticker - Query: {query}")
        existing_sticker = self.stickers.find_one(query)
        LOGS.debug(f"Database query result: {existing_sticker}")
        return existing_sticker

    def add_tags_to_sticker(self, user_id: int, sticker_unique_id: str, new_tags: list):
        """Add new tags to an existing sticker"""
        # Validate required fields
        if not sticker_unique_id:
            raise ValueError("sticker_unique_id cannot be empty or None")

        # Convert a single tag string to a list if needed
        if isinstance(new_tags, str):
            new_tags = [new_tags] if new_tags else []

        query = {
            "user_id": user_id,
            "sticker_unique_id": sticker_unique_id
        }
        # Use $addToSet to avoid duplicate tags
        update_data = {
            "$addToSet": {
                "tags": {"$each": new_tags}
            }
        }
        result = self.stickers.update_one(query, update_data)
        return result

    def update_sticker(self, user_id: int, sticker_unique_id: str, new_tags: list, new_emoji: str):
        """Update an existing sticker with new tags and emoji"""
        # Validate required fields
        if not sticker_unique_id:
            raise ValueError("sticker_unique_id cannot be empty or None")

        # Convert a single tag string to a list if needed
        if isinstance(new_tags, str):
            new_tags = [new_tags] if new_tags else []

        query = {
            "user_id": user_id,
            "sticker_unique_id": sticker_unique_id
        }
        update_data = {
            "$set": {
                "tags": new_tags,
                "emoji": new_emoji
            }
        }
        result = self.stickers.update_one(query, update_data)
        return result

    def get_recent_emojis(self, user_id: int, limit: int = 9):
        """Return the most recently used emojis for a user, most recent first."""
        docs = self.stickers.find(
            {"user_id": user_id, "emoji": {"$nin": ["", None]}},
            {"emoji": 1, "created_at": 1, "_id": 0},
        ).sort("created_at", -1)

        seen, recent = set(), []
        for doc in docs:
            emoji_value = doc.get("emoji")
            if emoji_value and emoji_value not in seen:
                seen.add(emoji_value)
                recent.append(emoji_value)
            if len(recent) >= limit:
                break
        return recent

    def get_random_sticker(self, user_id: int):
        """Return a random sticker document for a user, or None if the collection is empty."""
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$sample": {"size": 1}},
        ]
        docs = list(self.stickers.aggregate(pipeline))
        return docs[0] if docs else None

    def increment_sticker_use(self, user_id: int, sticker_unique_id: str):
        """Increment the use count of a sticker when it is sent via inline mode."""
        query = {
            "user_id": user_id,
            "sticker_unique_id": sticker_unique_id
        }
        result = self.stickers.update_one(query, {"$inc": {"use_count": 1}})
        return result

    def get_most_used_stickers(self, user_id: int, limit: int = 5):
        """Return the most-sent stickers for a user, most used first."""
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$addFields": {"use_count": {"$ifNull": ["$use_count", 0]}}},
            {"$sort": {"use_count": -1, "created_at": 1}},
            {"$limit": limit},
        ]
        return list(self.stickers.aggregate(pipeline))

    def get_stats(self, user_id: int, limit: int = 5):
        """Aggregate usage metrics for a user: sticker/tag/emoji popularity."""
        total = self.stickers.count_documents({"user_id": user_id})

        tagged_total = self.stickers.count_documents(
            {"user_id": user_id, "tags": {"$exists": True, "$ne": []}}
        )

        total_uses = self.stickers.aggregate([
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": None, "total": {"$sum": {"$ifNull": ["$use_count", 0]}}}},
        ])
        total_uses = next(total_uses, {}).get("total", 0)

        most_used_tags = list(self.stickers.aggregate([
            {"$match": {"user_id": user_id, "tags": {"$exists": True, "$ne": []}}},
            {"$unwind": "$tags"},
            {"$group": {"_id": "$tags", "uses": {"$sum": {"$ifNull": ["$use_count", 0]}}}},
            {"$sort": {"uses": -1, "_id": 1}},
            {"$limit": limit},
        ]))

        most_used_emojis = list(self.stickers.aggregate([
            {"$match": {"user_id": user_id, "emoji": {"$nin": ["", None]}}},
            {"$group": {"_id": "$emoji", "uses": {"$sum": {"$ifNull": ["$use_count", 0]}}}},
            {"$sort": {"uses": -1, "_id": 1}},
            {"$limit": limit},
        ]))

        return {
            "total_stickers": total,
            "total_uses": total_uses,
            "tagged_stickers": tagged_total,
            "most_used_stickers": self.get_most_used_stickers(user_id, limit),
            "most_used_tags": most_used_tags,
            "most_used_emojis": most_used_emojis,
        }