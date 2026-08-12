from app.database import database


class StateDB:
    """Persist per-user workflow state (StickerBot.USER_STATES) in MongoDB."""

    def __init__(self):
        db_instance = database()
        self.states = db_instance['user_states']

    def load(self, user_id: int):
        """Return the stored state dict for a user, or None if none exists."""
        record = self.states.find_one({"user_id": user_id})
        if record is None:
            return None
        record.pop('_id', None)
        record.pop('user_id', None)
        return record

    def save(self, user_id: int, data: dict):
        """Upsert the full state dict for a user."""
        doc = {"user_id": user_id}
        doc.update(data)
        self.states.replace_one({"user_id": user_id}, doc, upsert=True)

    def delete(self, user_id: int):
        """Remove any stored state for a user."""
        result = self.states.delete_one({"user_id": user_id})
        return result.deleted_count
