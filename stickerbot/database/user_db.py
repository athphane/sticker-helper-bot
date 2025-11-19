from datetime import datetime

from pyrogram.types import User as BaseUser

from stickerbot.database import database


class UserDB:
    def __init__(self):
        db_instance = database()
        # The database() function now returns the specific database, not the client
        self.users = db_instance['users']

    def find_user(self, from_user: BaseUser):
        query = {
            "id": from_user.id
        }
        record = self.users.find_one(query)
        return record

    def create_user(self, from_user: BaseUser):
        data = {
            "id": from_user.id,
            "f_name": from_user.first_name,
            "l_name": from_user.last_name,
            "username": from_user.username,
            'state': None,
            'created_at': datetime.now(),
        }
        self.users.insert_one(data)
        return self.find_user(from_user)

    def update_user(self, from_user: BaseUser):
        query = {
            "id": from_user.id,
        }

        data = {
            "f_name": from_user.first_name,
            "l_name": from_user.last_name,
            "username": from_user.username,
            "last_used": datetime.now()
        }

        new_values = {"$set": data}

        self.users.update_one(query, new_values)
        return self.find_user(from_user)

    def find_or_create(self, from_user: BaseUser):
        user = self.find_user(from_user)

        if user is None:
            self.create_user(from_user)
            user = self.find_user(from_user)

        return user