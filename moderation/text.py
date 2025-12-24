import asyncio
from database import users, badwords, is_group_verified
from utils import normalize
from config import OWNER_ID, DELETE_DELAY


# ---------------------------
# AUTO BADWORDS (NORMALIZED)
# ---------------------------
AUTO_BADWORDS = {
    # English
    "fuck", "fucking", "shit", "bitch", "asshole", "dick", "pussy",
    "porn", "sex", "nude", "xxx", "boobs", "blowjob",

    # Hindi / Hinglish
    "bhosdike", "bhosdi", "bhosda",
    "madarchod", "behenchod",
    "chutiya", "chut", "lund",
    "gaand", "gand", "randi",
    "harami", "kamina",

    # Short forms (handled carefully)
    "bc", "mc", "bdsk"
}

AUTO_BADWORDS = {normalize(w) for w in AUTO_BADWORDS}


# ---------------------------
# DELETE MESSAGE AFTER DELAY
# ---------------------------
async def delete_later(context, chat_id, msg_id):
    await asyncio.sleep(DELETE_DELAY)
    try:
        await context.bot.delete_message(chat_id, msg_id)
    except Exception:
        pass


# ---------------------------
# MAIN TEXT MONITOR
# ---------------------------
async def monitor_text(update, context):
    msg = update.message
    if not msg or not msg.text:
        return

    chat = msg.chat

    # ❌ Ignore private chats
    if chat.type == "private":
        return

    # ❌ Group not verified
    if not is_group_verified(chat.id):
        return

    user = msg.from_user

    # 👑 Owner bypass
    if user.id == OWNER_ID:
        return

    # ✅ Approved user bypass
    if users.find_one({"user_id": user.id, "approved": True}):
        return

    text = normalize(msg.text)

    # ---------------------------
    # AUTO BADWORDS CHECK
    # ---------------------------
    for word in AUTO_BADWORDS:
        # short words need exact containment
        if len(word) <= 3:
            if text == word or text.startswith(word) or text.endswith(word):
                context.application.create_task(
                    delete_later(context, chat.id, msg.message_id)
                )
                return
        else:
            if word in text:
                context.application.create_task(
                    delete_later(context, chat.id, msg.message_id)
                )
                return

    # ---------------------------
    # MANUAL BADWORDS FROM DB
    # ---------------------------
    for bw in badwords.find({}, {"word": 1}):
        if bw["word"] in text:
            context.application.create_task(
                delete_later(context, chat.id, msg.message_id)
            )
            return
