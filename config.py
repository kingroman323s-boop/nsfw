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

DELETE_DELAY = 1

