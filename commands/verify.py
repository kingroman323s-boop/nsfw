from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes
import config
from database import verify_group, is_group_verified


async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 👑 Owner only
    if update.effective_user.id != config.OWNER_ID:
        return

    if not context.args:
        await update.message.reply_text(
            "❌ Usage:\n/verify <group_id>\n\nExample:\n/verify -1001234567890"
        )
        return

    try:
        group_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid group ID")
        return

    # Already verified
    if is_group_verified(group_id):
        await update.message.reply_text("⚠️ This group is already verified")
        return

    # ✅ Verify group
    verify_group(group_id)

    # Unverify button
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚫 Unverify", callback_data=f"unverify:{group_id}")]
    ])

    # Owner confirmation
    await update.message.reply_text(
        f"✅ *Group Verified Successfully*\n\n🆔 `{group_id}`",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

    # Notify the group itself
    try:
        await context.bot.send_message(
            chat_id=group_id,
            text=(
                "✅ *This group has been verified*\n\n"
                "Moderation is now active.\n"
                "NSFW, bad words & spam will be filtered."
            ),
            parse_mode="Markdown"
        )
    except Exception:
        pass

    # Log
    try:
        await context.bot.send_message(
            chat_id=config.LOG_GROUP_ID,
            text=(
                "✅ *Group Verified*\n\n"
                f"🆔 ID: `{group_id}`\n"
                f"👑 Verified by: `{update.effective_user.id}`"
            ),
            parse_mode="Markdown"
        )
    except Exception:
        pass
