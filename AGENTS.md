# AGENTS.md

## Project Overview
Telegram bot for saving, tagging, and searching stickers, built with Kurigram (an actively-maintained Pyrogram fork that installs as the `pyrogram` module — a drop-in replacement). Each user has their own sticker collection stored in MongoDB. Users send a sticker, tag it with words + an emoji, and later retrieve it via inline mode (`@stickerdexbot <tag>`). Stickers are deduplicated per user via `file_unique_id`; re-sending one already in your collection opens an edit flow instead of a duplicate save.

## Architecture
- **`app/bot.py`** — `StickerBot` class extends Kurigram's `Client`. Session name `stickerbot`, `workdir="./workdir"`, `workers=16`, plugins root `"app/plugins"`. Per-user workflow state lives in `USER_STATES` (a process-wide cache keyed by `user_id`) and is persisted to MongoDB's `user_states` collection via a shared `StateDB` (`app/database/state_db.py`): read-through on cache miss, write-through on every setter, so restarts resume in-progress workflows. Getters/setters: `get/set_sticker_state`, `get/set_sticker_id`, `get/set_sticker_unique_id`, `get/set_error_message_id`, `get/set_tag`, `get/set_emoji`, plus `clear_user_state(user_id)` (drops the Mongo doc + cache). `start()` registers bot commands (`/start`, `/help`, `/clear`, `/random`, `/collection`, `/import`) via `set_bot_commands`; `stop()` calls `close_connection()` to release the Mongo pool.
- **`app/__init__.py`** — module globals: logging (INFO level, `TimedRotatingFileHandler` → `logs/app.log` rotating at midnight, 10 backups, plus a StreamHandler), config parsing (`config.ini`), constants (`TELEGRAM_API_ID/HASH/TOKEN`, `TELEGRAM_ADMINS` (list of int), `MONGO_URL`, `MONGO_USERNAME`, `MONGO_PASSWORD`, `MONGO_DB_NAME` (default `stickerbot`), `MONGO_DB_AUTH_SOURCE`). `__version__ = '1.0.0'`, `__author__ = 'Athfan Khaleel'`. Instantiates the `StickerBot`.
- **`app/__main__.py`** — entry point (`python -m app`). Imports `StickerBot` from `app` then runs.
- **`app/plugins/`** — Kurigram handlers: `start.py`, `save_sticker.py` (saving + editing + confirmation + callbacks), `inline.py`, `library.py` (`/random`, `/collection` browser with `browse_*` callbacks), `import_pack.py` (pack import via `t.me/addstickers` links). Each defines a module-level `user_db = UserDB()` instance.
- **`app/database/`** — `__init__.py` holds a **process-wide shared, lazily-created `MongoClient` singleton** (`get_client()`, thread-safe double-checked lock) tuned via `POOL_OPTIONS` (maxPoolSize 20, minPoolSize 1, maxIdleTimeMS 30s, connectTimeoutMS 10s, serverSelectionTimeoutMS 5s, appname `sticker-helper-bot`). `database()` returns the shared db handle; `close_connection()` closes the pool on shutdown. Plus `StickerDB` and `UserDB` classes.
- **`app/helpers/`** — `sticker_manager.py` (static `StickerManager` wrappers over a module-level shared `_db = StickerDB()` instance), `sticker_state_enum.py`, `string_parsers.py`, `keyboard_utils.py`.

## Workflow / State Machine
Per-user state lives in `StickerBot.USER_STATES[user_id]['state']` (persisted to Mongo's `user_states` collection, keyed by `user_id`), values from `StickerStates` (int enum): `NOTHING → WAITING_FOR_TAG → SELECTING_EMOJI → CONFIRMING_STICKER`, plus `WAITING_FOR_EMOJI`, `SAVING_STICKER`, `EDITING_EXISTING_STICKER`, `ADDING_TAGS` (add-more-tags after save).

1. `/start` (`plugins/start.py:12`) — `UserDB.find_or_create` the user, shows sticker count + main reply keyboard.
2. User sends a sticker (`plugins/save_sticker.py:26`):
   - `sticker_id` (file_id) stored for re-sending; `sticker_unique_id` used for duplicate detection.
   - If `sticker_exists(user_id, sticker_unique_id)` → state `EDITING_EXISTING_STICKER`, shows current details + inline keyboard Edit Tag / Edit Emoji / Edit Both / Cancel (`edit_existing_*` callbacks).
   - New sticker → `WAITING_FOR_TAG`, shows the tag reply keyboard.
3. Tags (`set_tag` handler at `save_sticker.py:92`, matches text not starting with `/`): multiple, comma/space separated, parsed/validated by `parse_tags` / `validate_tag`. Buttons: `Skip Tags`, `Help with Tags`, `Cancel`. Valid tags → `SELECTING_EMOJI`.
4. Emoji: inline keyboard of common emojis (`emoji_<EMOJI>` callbacks, `keyboard_utils.get_common_emojis_keyboard`) or typed directly (both `WAITING_FOR_EMOJI` and `SELECTING_EMOJI` text branches are identical). Buttons: `Recent Emojis`, `Skip Emoji`. → `CONFIRMING_STICKER`.
5. Confirmation: sticker re-sent with inline keyboard Confirm / Cancel / Edit Tag / Edit Emoji (`confirm_save`, `cancel_save`, `edit_tag`, `edit_emoji`). `confirm_save` → `handle_sticker_saving_with_user_id` which inserts (new) or updates (existing) in Mongo.
6. Editing an existing sticker (via `edit_existing_*` callbacks): reuses the same tag/emoji/confirm flow; the final confirm updates the doc by `sticker_unique_id`.
7. Inline search (`plugins/inline.py:13`): `find_stickers_like` → regex `$elemMatch` on `tags` array or exact match on `emoji`, always filtered by `user_id`; returns `InlineQueryResultCachedSticker` with `is_gallery=True`, `cache_time=1`. Empty results return a "no stickers found" article.
8. `/clear` (`save_sticker.py:14`) — drops the persisted state (`clear_user_state`) and returns the main keyboard.
9. Add more tags (`ADDING_TAGS`, `save_sticker.py`): after a successful save the reply keyboard offers "Add More Tags", which appends new tags to the just-saved sticker via `add_tags_to_sticker` (`$addToSet`).

## Database
- Collections: `stickers` (fields: `user_id`, `sticker_id`, `sticker_unique_id`, `tags` (list), `emoji`, `created_at`), `users` (`id`, `f_name`, `l_name`, `username`, `created_at`, `last_used`, `state`), and `user_states` (workflow state, keyed by `user_id`).
- Every sticker query is scoped by `user_id` — never query stickers without it.
- `file_unique_id` is the canonical identity for a sticker (a sticker sent from different sources has a different `file_id` but same `file_unique_id`).
- `StickerDB` methods: `all_stickers`, `find_sticker`, `find_stickers_by_user`, `find_stickers_like` (`limit` default 50, supports `offset` for pagination), `insert_sticker`, `delete_sticker`, `get_user_sticker_count`, `sticker_exists`, `add_tags_to_sticker` (`$addToSet`), `update_sticker` (`$set` tags + emoji), `get_recent_emojis`, `get_random_sticker` (`$sample`).
- One shared MongoClient + one shared `StickerDB`/`UserDB`/`StateDB` per process — do not instantiate new clients/db wrappers per request.

## Config (`config.ini`)
Required sections (template in `config.ini.example`):
```ini
[telegram]
api_id = your_api_id
api_hash = your_api_hash
bot_token = your_bot_token
admins = 123456789

[mongo]
url = mongodb:27017
username = admin
password = your_secure_password
db_name = stickerbot
auth_source = admin
```
`config.ini` exists in this checkout but is gitignored (`config.ini`, `*.session`, `logs/`, `workdir/` in `.gitignore`). The `url = mongodb:27017` matches the `mongodb` service hostname in `docker-compose.yml`.

## Commands
- `/start` — welcome + sticker count.
- `/help` — how to use the bot.
- `/clear` — reset current saving process / state.
- `/random` — send a random sticker from your collection (also a main-keyboard button "Random Sticker").
- `/collection` — browse your collection one sticker per page with Prev / Next / Delete / Edit / Close (`browse_*` callbacks in `library.py`).
- `/import` — import a whole sticker pack from a `t.me/addstickers/...` link (also triggers on pasted links). Uses Kurigram's `get_stickers(short_name)`; each sticker is saved with the pack name as a tag and its own emoji, deduped by `file_unique_id`.

## Build & Run
1. `pip install -r requirements.txt` (`kurigram` (installs as the `pyrogram` module), `tgcrypto`, `emoji`, `pymongo`)
2. Create `config.ini` from `config.ini.example` (see above)
3. `python -m app`

## Docker
- `Dockerfile` — python:3.12-slim, installs `gcc`/`libc-dev` (needed for tgcrypto), `CMD ["python", "-m", "app"]`.
- `docker-compose.yml` — spins up `mongodb` + `app` on a shared `bot-network`. Mounts `./config.ini`, `./workdir`, `./logs` into the container.
- `workdir/` holds the Kurigram session file (`stickerbot.session`); `logs/` holds rotated app logs; both are gitignored and persist on the host.
- Run: `docker compose up -d --build`. The Mongo root user in `docker-compose.yml` must match `[mongo]` in `config.ini`; `auth_source = admin` is used for the root user.

## Git History
4 commits on `main` (ahead of `origin/main` by 2, unpushed):
- `b8c3bf8` — "- init"
- `ec210c2` — "update whole project to support multi users and multi tags per sticker"
- `4031154` — "Restructure project to match athphane-bot conventions" (renamed `stickerbot/` → `app/`, added Docker + `config.ini.example`, `[telegram]`/`[mongo]` config sections)
- `296d81d` — "Share a single MongoDB connection pool instead of one client per call" (shared singleton client + shared `StickerDB`/`UserDB` instances)

## Known Issues / Notes (from code review + runtime)
- `logs/app.log` shows the bot has run successfully on Kurigram (Layer 227, `@stickerdexbot`).
- **Remaining drift / legacy states**:
  - `StickerStates.WAITING_FOR_EMOJI` and `SAVING_STICKER` are legacy states; `WAITING_FOR_EMOJI` is still handled together with `SELECTING_EMOJI` for backward compatibility.
  - `helpers/string_parsers.py` `is_text()` is unused (only `parse_tags`, `validate_tag`, `is_emoji` are used).
  - Search is substring-regex on `tags` and exact-match on `emoji`; no tokenized (AND) matching yet.
- Inline search now supports pagination via `next_offset` (`PAGE_SIZE = 50` in `inline.py`) and sets `is_personal=True`.

## Conventions
- Kurigram plugin pattern (`@StickerBot.on_message`, `@StickerBot.on_callback_query`, `@StickerBot.on_inline_query`). Text-button handlers that would be swallowed by `save_sticker.set_tag`'s catch-all filter (`^(?!/)`) are registered with `group=-1` for higher dispatch priority (e.g. "Random Sticker", "My Collection", pack links, "Recent Emojis", "Skip Emoji").
- Type hints used.
- Per-user isolation everywhere.
- Debugging via `logging` (`LOGS = logging.getLogger(__name__)` per module); `print()` has been removed from handlers/db layers.
- Reuse the module-level shared `user_db` / `_db` / `_state_db` instances rather than instantiating new ones per request.
