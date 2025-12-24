import asyncio
from database import users, badwords, is_group_verified
from utils import normalize
from config import OWNER_ID, DELETE_DELAY


# ─────────────────────────────────────────────
# AUTO BADWORDS (NORMALIZED)
# ─────────────────────────────────────────────
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

    # Short forms
    "bc", "mc", "bdsk"
}

AUTO_BADWORDS = {normalize(w) for w in AUTO_BADWORDS}


# ─────────────────────────────────────────────
# SAFE DELETE TASK
# ─────────────────────────────────────────────
async def delete_later(bot, chat_id, msg_id, delay=DELETE_DELAY):
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(chat_id, msg_id)
    except Exception:
        pass


# ─────────────────────────────────────────────
# MAIN TEXT MONITOR
# ─────────────────────────────────────────────
async def monitor_text(update, context):
    msg = update.message
    if not msg or not msg.text:
        return

    chat = msg.chat

    # Ignore private chats
    if chat.type == "private":
        return

    # Group not verified
    if not is_group_verified(chat.id):
        return

    user = msg.from_user

    # Owner bypass
    if user.id == OWNER_ID:
        return

    # Approved user bypass
    if users.find_one({"user_id": user.id, "approved": True}):
        return

    text = normalize(msg.text)

    # ─────────────────────────────────────────
    # AUTO BADWORDS CHECK
    # ─────────────────────────────────────────
    for word in AUTO_BADWORDS:
        detected = False

        if len(word) <= 3:
            if f" {word} " in f" {text} ":
                detected = True
        else:
            if word in text:
                detected = True

        if detected:
            # Warning message
            warn_msg = await context.bot.send_message(
                chat_id=chat.id,
                text=(
                    "⚠️ <b>Warning</b>\n\n"
                    f"Your message will be deleted in "
                    f"<b>{DELETE_DELAY}</b> seconds."
                ),
                parse_mode="HTML",
                reply_to_message_id=msg.message_id
            )

            # Schedule deletions
            context.application.create_task(
                delete_later(context.bot, chat.id, msg.message_id)
            )
            context.application.create_task(
                delete_later(context.bot, chat.id, warn_msg.message_id)
            )
            return

    # ─────────────────────────────────────────
    # DATABASE BADWORDS CHECK
    # ─────────────────────────────────────────
    for bw in badwords.find({}, {"word": 1}):
        bw_word = normalize(bw["word"])
        if bw_word in text:
            warn_msg = await context.bot.send_message(
                chat_id=chat.id,
                text=(
                    "⚠️ <b>Warning</b>\n\n"
                    f"Your message will be deleted in "
                    f"<b>{DELETE_DELAY}</b> seconds."
                ),
                parse_mode="HTML",
                reply_to_message_id=msg.message_id
            )

            context.application.create_task(
                delete_later(context.bot, chat.id, msg.message_id)
            )
            context.application.create_task(
                delete_later(context.bot, chat.id, warn_msg.message_id)
            )
            return
