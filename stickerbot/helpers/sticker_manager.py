from supabase import Client as SupabaseClient
from supabase import create_client as sb_create_client

from stickerbot import SUPABASE_URL, SUPABASE_KEY

supabase: SupabaseClient = sb_create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

stickers_table = supabase.table('stickers')


class StickerManager:
    @staticmethod
    def insert_sticker(sticker_id: str, tag: str, emoji: str):
        return stickers_table.insert({
            "sticker_id": sticker_id,
            "tag": tag,
            "emoji": emoji,
        }).execute()

    @staticmethod
    def all_stickers_like(search: str, limit: int = 10):
        return stickers_table.select("*").or_(f"tag.ilike.%{search}%,emoji.eq.{search}").limit(limit).execute()
