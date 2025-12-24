from telegram import Update
from telegram.ext import ContextTypes
import config
from database import unverify_group


async def unverify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user

    # 👑 Owner only
    if user.id != config.OWNER_ID:
        await query.answer("Not authorized", show_alert=True)
        return

    data = query.data

    if not data.startswith("unverify:"):
        return

    try:
        group_id = int(data.split(":")[1])
    except ValueError:
        return

    # 🚫 Unverify
    unverify_group(group_id)

    # Update button message
    await query.edit_message_text(
        text=(
            "🚫 *Group Unverified*\n\n"
            f"🆔 `{group_id}`\n"
            "Moderation disabled."
        ),
        parse_mode="Markdown"
    )

    # Notify group
    try:
        await context.bot.send_message(
            chat_id=group_id,
            text="🚫 *This group has been unverified*\n\nModeration is now disabled.",
            parse_mode="Markdown"
        )
    except Exception:
        pass

    # Log
    try:
        await context.bot.send_message(
            chat_id=config.LOG_GROUP_ID,
            text=(
                "🚫 *Group Unverified (Button)*\n\n"
                f"🆔 ID: `{group_id}`\n"
                f"👑 By: `{user.id}`"
            ),
            parse_mode="Markdown"
        )
    except Exception:
        pass
