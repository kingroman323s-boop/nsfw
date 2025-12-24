import asyncio
from database import users, badwords, is_group_verified
from utils import normalize
from config import OWNER_ID, DELETE_DELAY


AUTO_BADWORDS = {
    "fuck", "fucking", "shit", "bitch", "asshole", "dick", "pussy",
    "porn", "sex", "nude", "xxx", "boobs", "blowjob",
    "bhosdike", "bhosdi", "bhosda",
    "madarchod", "behenchod",
    "chutiya", "chut", "lund",
    "gaand", "gand", "randi",
    "harami", "kamina",
    "bc", "mc", "bdsk"
}

AUTO_BADWORDS = {normalize(w) for w in AUTO_BADWORDS}


# ─────────────────────────────────────────────
# DELETE TASK (WITH LOGGING)
# ─────────────────────────────────────────────
async def delete_later(bot, chat_id, msg_id, delay=DELETE_DELAY):
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(chat_id, msg_id)
    except Exception as e:
        print(f"❌ Delete failed: {e}")


# ─────────────────────────────────────────────
# MAIN MONITOR
# ─────────────────────────────────────────────
async def monitor_text(update, context):
    msg = update.message
    if not msg or not msg.text:
        return

    chat = msg.chat
    if chat.type == "private":
        return

    if not is_group_verified(chat.id):
        return

    user = msg.from_user
    if user.id == OWNER_ID:
        return

    if users.find_one({"user_id": user.id, "approved": True}):
        return

    text = normalize(msg.text)

    # BADWORD CHECK
    detected = False
    for word in AUTO_BADWORDS:
        if len(word) <= 3:
            if f" {word} " in f" {text} ":
                detected = True
                break
        else:
            if word in text:
                detected = True
                break

    if not detected:
        for bw in badwords.find({}, {"word": 1}):
            if normalize(bw["word"]) in text:
                detected = True
                break

    if not detected:
        return

    # ─────────────────────────────────────────
    # SEND WARNING (NO REPLY MODE)
    # ─────────────────────────────────────────
    try:
        warn_msg = await context.bot.send_message(
            chat_id=chat.id,
            text=(
                "⚠️ <b>Warning</b>\n\n"
                f"This message violates rules and will be deleted in "
                f"<b>{DELETE_DELAY}</b> seconds."
            ),
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"❌ Warning send failed: {e}")
        return

    # ─────────────────────────────────────────
    # SCHEDULE DELETIONS
    # ─────────────────────────────────────────
    context.application.create_task(
        delete_later(context.bot, chat.id, msg.message_id)
    )
    context.application.create_task(
        delete_later(context.bot, chat.id, warn_msg.message_id)
    )

