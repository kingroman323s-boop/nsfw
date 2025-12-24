import os

# ─────────────────────────────────────────────
# REQUIRED ENVIRONMENT VARIABLES (RENDER)
# ─────────────────────────────────────────────

BOT_TOKEN = os.environ.get("BOT_TOKEN")
MONGO_URI = os.environ.get("MONGO_URI")

OWNER_ID = int(os.environ.get("OWNER_ID", 0))
LOG_GROUP_ID = int(os.environ.get("LOG_GROUP_ID", 0))
SUPPORT_CHAT_ID = int(os.environ.get("SUPPORT_CHAT_ID", 0))

RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")

# ─────────────────────────────────────────────
# OPTIONAL / CONSTANT SETTINGS
# ─────────────────────────────────────────────

DELETE_DELAY = 120

# # PYTHON_VERSION=3.10.13

# DELETE_DELAY = 120
# SUPPORT_CHAT_ID=-1002641745655
# BOT_TOKEN="8179093437:AAFEuViafDkyWyjDkwOOBIxoZT2gsaLV_AI"
# MONGO_URI="mongodb+srv://rudraxgame_db_user:Rudrax0607@gamblebot.iw8dger.mongodb.net/?appName=GAMBLEBOT"
# OWNER_ID=7562158122

# # RENDER_EXTERNAL_URL="https://nsfw-h3r0.onrender.com"
# LOG_GROUP_ID=-1002641745655