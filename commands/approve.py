from database import users
from config import OWNER_ID

async def approve(update, context):
    if update.effective_user.id != OWNER_ID:
        return

    reply = update.message.reply_to_message
    if not reply:
        return

    users.update_one(
        {"user_id": reply.from_user.id},
        {"$set": {"approved": True}},
        upsert=True
    )

    await update.message.reply_text("✅ User approved")
