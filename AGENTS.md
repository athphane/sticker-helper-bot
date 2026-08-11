# AGENTS.md

## Project Overview
Telegram bot for saving, tagging, and searching stickers, built with Pyrogram. Each user has their own sticker collection stored in MongoDB. Users send a sticker, tag it with words + an emoji, and later retrieve it via inline mode (`@yourbot <tag>`).

## Architecture
- **`app/bot.py`** — `StickerBot` class extends Pyrogram's `Client`. Holds per-user workflow state in `USER_STATES` dict (in-memory, keyed by `user_id`) with getter/setter helpers.
- **`app/__init__.py`** — module globals: logging setup (rotates to `logs/app.log`), config parsing, `StickerBot` instance, constants (`TELEGRAM_ADMINS`, `MONGO_URL`, etc.).
- **`app/__main__.py`** — entry point (`python -m app`). Imports the `StickerBot` instance from `app` then runs.
- **`app/plugins/`** — Pyrogram handlers: `start.py`, `save_sticker.py`, `inline.py`.
- **`app/database/`** — `database()` connection factory + `StickerDB`, `UserDB` classes.
- **`app/helpers/`** — `sticker_manager.py` (static wrappers over `StickerDB`), `sticker_state_enum.py`, `string_parsers.py`, `keyboard_utils.py`.

## Workflow / State Machine
Per-user state lives in `StickerBot.USER_STATES[user_id]['state']`, values from `StickerStates` enum:
`NOTHING → WAITING_FOR_TAG → SELECTING_EMOJI → CONFIRMING_STICKER → done`, plus `WAITING_FOR_EMOJI`, `SAVING_STICKER`, `EDITING_EXISTING_STICKER` (legacy, mostly unused).

1. `/start` — creates/updates user in `users` collection, shows sticker count + main keyboard.
2. User sends a sticker (`plugins/save_sticker.py:24`):
   - `file_id` stored for re-sending; `file_unique_id` used for duplicate detection.
   - If it already exists for the user → inline keyboard offers Edit Tag / Edit Emoji / Edit Both (callbacks `edit_existing_*`).
   - New sticker → `WAITING_FOR_TAG`.
3. Tags: multiple, comma/space separated, parsed/validated by `parse_tags` / `validate_tag` in `helpers/string_parsers.py`.
4. Emoji: inline keyboard of common emojis (callback `emoji_<EMOJI>`) or typed directly.
5. Confirmation: sticker re-sent with Confirm / Cancel / Edit Tag / Edit Emoji callbacks (`confirm_save`, `cancel_save`, `edit_tag`, `edit_emoji`).
6. Inline search (`plugins/inline.py`): regex search on `tags` array or exact match on `emoji`, always filtered by `user_id`; returns `InlineQueryResultCachedSticker`.

## Database
- Collections: `stickers` (fields: `user_id`, `sticker_id`, `sticker_unique_id`, `tags` (list), `emoji`) and `users` (id, f_name, l_name, username, created_at, last_used).
- Every sticker query is scoped by `user_id` — never query stickers without it.
- `file_unique_id` is the canonical identity for a sticker (a sticker sent from different sources has a different `file_id` but same `file_unique_id`).

## Config (`config.ini`)
Required sections (template in `config.ini.example`):
```ini
[telegram]
api_id = ...
api_hash = ...
bot_token = ...
admins = ADMIN_USER_ID_1,ADMIN_USER_ID_2

[mongo]
url = YOUR_MONGODB_URL
username = ...
password = ...
db_name = stickerbot
auth_source = admin
```

## Commands
- `/start` — welcome + sticker count.
- `/clear` — reset current saving process / state.

## Build & Run
1. `pip install -r requirements.txt` (`pyrogram`, `tgcrypto`, `emoji`, `pymongo`)
2. Create `config.ini` from `config.ini.example` (see above)
3. `python -m app`

## Docker
- `Dockerfile` — python:3.12-slim, installs `gcc`/`libc-dev` (needed for tgcrypto), `CMD ["python", "-m", "app"]`.
- `docker-compose.yml` — spins up `mongodb` + `app` on a shared `bot-network`. Mounts `./config.ini`, `./workdir`, `./logs` into the container.
- `workdir/` holds the Pyrogram session file; `logs/` holds rotated app logs; both are gitignored and persist on the host.
- Run: `docker compose up -d --build`. The Mongo root user in `docker-compose.yml` must match `[mongo]` in `config.ini`; `auth_source = admin` is used for the root user.

## Known Issues / Notes (from code review)
- **`config.ini` is not committed** and missing in this checkout; bot cannot run without it (copy `config.ini.example`).
- **`logs/` dir is empty** — bot has likely never been successfully run from this checkout.
- **Dead code / drift**:
  - `helpers/string_parsers.py` `is_text()` is unused.
  - `plugins/save_sticker.py` has two identical tag-handling branches (`WAITING_FOR_EMOJI` at ~137 and `SELECTING_EMOJI` at ~165) with duplicated code.
  - The `EDITING_EXISTING_STICKER` text branch in `set_tag` is an empty `pass`; actual editing is handled via callbacks.
  - `helpers/sticker_manager.py` — most static methods use `print()` for errors instead of the configured logger; `sticker_exists` in `sticker_db.py` also uses `print`.
  - `StickerStates.WAITING_FOR_EMOJI` and `SAVING_STICKER` are legacy states.
  - `confirm_update` callback handler exists but the UI never produces `confirm_update` callback data.
- **Git history**: only 2 commits ("- init", "update whole project to support multi users and multi tags per sticker").
- In-memory state (`USER_STATES`) means bot restarts wipe all in-progress workflows — no persistence of state.

## Conventions
- Pyrogram plugin pattern (`@StickerBot.on_message`, etc.).
- Type hints used.
- Per-user isolation everywhere.
- Debugging done via `print()` in plugins/handlers (logging configured but not consistently used).
