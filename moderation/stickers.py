from database import users, stickers
from database import is_group_verified
from config import OWNER_ID, DELETE_DELAY
from moderation.text import delete_later


# ---------------------------
# AUTO NSFW HEURISTICS
# ---------------------------
NSFW_KEYWORDS = {
    "18", "sex", "nsfw", "adult",
    "xxx", "hentai", "nude", "porn",
    "boobs", "hot", "fuck"
}

NSFW_EMOJIS = {
    "🍑", "🍆", "💦", "🔥", "😈", "🥵", "👅"
}


def looks_nsfw(sticker) -> bool:
    name = (sticker.set_name or "").lower()
    emoji = sticker.emoji or ""

    if any(k in name for k in NSFW_KEYWORDS):
        return True

    if any(e in emoji for e in NSFW_EMOJIS):
        return True

    return False


async def monitor_sticker(update, context):
    msg = update.message
    if not msg or not msg.sticker:
        return

    chat = msg.chat

    # ❌ Ignore private chats
    if chat.type == "private":
        return

    # ❌ Ignore unverified groups
    if not is_group_verified(chat.id):
        return

    user = msg.from_user

    # 👑 Owner bypass
    if user.id == OWNER_ID:
        return

    # ✅ Approved users bypass
    if users.find_one({"user_id": user.id, "approved": True}):
        return

    sticker = msg.sticker

    # 🔥 AUTO NSFW DETECTION
    if looks_nsfw(sticker):
        context.application.create_task(
            delete_later(context, chat.id, msg.message_id)
        )
        return

    # 🔥 MANUAL BLOCK: STICKER PACK
    if sticker.set_name:
        if stickers.find_one({"type": "pack", "value": sticker.set_name}):
            context.application.create_task(
                delete_later(context, chat.id, msg.message_id)
            )
            return

    # 🔥 MANUAL BLOCK: SINGLE STICKER
    if stickers.find_one({"type": "single", "value": sticker.file_unique_id}):
        context.application.create_task(
            delete_later(context, chat.id, msg.message_id)
        )
