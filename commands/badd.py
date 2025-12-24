from telegram import Update
from telegram.ext import ContextTypes
from database import badwords
from config import OWNER_ID, LOG_GROUP_ID
from utils import normalize


async def badd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 👑 Owner only
    if update.effective_user.id != OWNER_ID:
        return

    text = update.message.text.replace("/badd", "", 1).strip()

    if not text:
        await update.message.reply_text(
            "❌ Usage:\n/badd word1, word2, word3"
        )
        return

    raw_words = [w.strip() for w in text.split(",")]
    added = []

    for raw in raw_words:
        norm = normalize(raw)

        if not norm:
            continue

        # avoid duplicates
        if badwords.find_one({"word": norm}):
            continue

        badwords.insert_one({"word": norm})
        added.append(norm)

    if not added:
        await update.message.reply_text("⚠️ No new bad words added")
        return

    # ✅ Confirmation to owner
    await update.message.reply_text(
        "✅ *Bad words added:*\n" + "\n".join(f"• `{w}`" for w in added),
        parse_mode="Markdown"
    )

    # 🧾 Log
    try:
        await context.bot.send_message(
            chat_id=LOG_GROUP_ID,
            text=(
                "🚫 *Bad Words Added*\n\n"
                + "\n".join(f"• `{w}`" for w in added)
            ),
            parse_mode="Markdown"
        )
    except Exception:
        pass
