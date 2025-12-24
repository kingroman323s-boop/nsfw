from telegram import Update
from telegram.ext import ContextTypes
from database import stickers
from config import OWNER_ID, LOG_GROUP_ID


async def bstick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Owner only
    if update.effective_user.id != OWNER_ID:
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a sticker")
        return

    msg = update.message.reply_to_message
    if not msg.sticker:
        await update.message.reply_text("❌ That is not a sticker")
        return

    st = msg.sticker

    # 📦 Block entire pack
    if st.set_name:
        stickers.update_one(
            {"type": "pack", "value": st.set_name},
            {"$set": {"type": "pack", "value": st.set_name}},
            upsert=True
        )

        await update.message.reply_text("📦 *Sticker pack blocked*", parse_mode="Markdown")

        await context.bot.send_message(
            chat_id=LOG_GROUP_ID,
            text=f"📦 *Sticker Pack Blocked*\n\n`{st.set_name}`",
            parse_mode="Markdown"
        )

    # 🧩 Block single sticker
    else:
        stickers.update_one(
            {"type": "single", "value": st.file_unique_id},
            {"$set": {"type": "single", "value": st.file_unique_id}},
            upsert=True
        )

        await update.message.reply_text("🧩 *Sticker blocked*", parse_mode="Markdown")

        await context.bot.send_message(
            chat_id=LOG_GROUP_ID,
            text=f"🧩 *Sticker Blocked*\n\nID: `{st.file_unique_id}`",
            parse_mode="Markdown"
        )
