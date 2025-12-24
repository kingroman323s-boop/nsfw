import os
import asyncio
from aiohttp import web, ClientSession

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    ChatMemberHandler,
    filters,
    Application,
    ContextTypes,
)

import config
from config import BOT_TOKEN
from database import is_group_verified, unverify_group

from commands.verify import verify
from commands.approve import approve
from commands.badd import badd
from commands.bstick import bstick

from moderation.text import monitor_text
from moderation.stickers import monitor_sticker
from moderation.images import monitor_images


# ─────────────────────────────────────────────
# BOT ADDED TO GROUP HANDLER
# ─────────────────────────────────────────────
async def on_bot_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    member = update.chat_member

    if member.new_chat_member.user.id != context.bot.id:
        return

    if is_group_verified(chat.id):
        return

    inviter = member.from_user
    invite_link = chat.invite_link or "No public link"

    await context.bot.send_message(
        chat_id=chat.id,
        text=(
            "⚠️ <b>Group Not Verified</b>\n\n"
            "This bot will not work until your group is verified.\n\n"
            "👉 Please contact the owner."
        ),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👑 Contact Owner", url=f"tg://user?id={config.OWNER_ID}")]
        ])
    )

    log_text = (
        "<b>➕ Bot Added To Group</b>\n\n"
        f"📛 <b>Group:</b> {chat.title}\n"
        f"🆔 <b>ID:</b> <code>{chat.id}</code>\n"
        f"👤 <b>Added by:</b> {inviter.mention_html()}\n"
        f"🔗 <b>Link:</b> {invite_link}"
    )

    try:
        await context.bot.send_message(
            chat_id=config.LOG_GROUP_ID,
            text=log_text,
            parse_mode="HTML"
        )
    except Exception:
        pass


# ─────────────────────────────────────────────
# UNVERIFY BUTTON HANDLER
# ─────────────────────────────────────────────
async def unverify_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != config.OWNER_ID:
        await query.answer("❌ Owner only", show_alert=True)
        return

    if not query.data.startswith("unverify:"):
        return

    try:
        group_id = int(query.data.split(":")[1])
    except Exception:
        return

    unverify_group(group_id)

    text = f"🚫 <b>Group Unverified</b>\n\n🆔 <code>{group_id}</code>"

    await query.edit_message_text(text, parse_mode="HTML")

    try:
        await context.bot.send_message(
            chat_id=config.LOG_GROUP_ID,
            text=text,
            parse_mode="HTML"
        )
    except Exception:
        pass


# ─────────────────────────────────────────────
# WEB SERVER (RENDER HEALTH CHECK)
# ─────────────────────────────────────────────
async def handle(request):
    application: Application = request.app["telegram_app"]

    try:
        await application.bot.send_message(
            chat_id=config.LOG_GROUP_ID,
            text="📡 Bot is alive (Render ping)"
        )
    except Exception:
        pass

    return web.Response(text="Bot is alive ✅")


async def start_webserver(application: Application):
    app_web = web.Application()
    app_web["telegram_app"] = application
    app_web.add_routes([web.get("/", handle)])

    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app_web)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    print(f"🌐 Web server running on port {port}")


# ─────────────────────────────────────────────
# SELF PING (RENDER)
# ─────────────────────────────────────────────
async def keep_alive():
    url = os.environ.get("RENDER_EXTERNAL_URL")
    if not url:
        print("⚠️ RENDER_EXTERNAL_URL not set")
        return

    async with ClientSession() as session:
        while True:
            try:
                async with session.get(url):
                    pass
            except Exception:
                pass
            await asyncio.sleep(300)  # 5 minutes


# ─────────────────────────────────────────────
# POST INIT (THIS WAS THE MAIN BUG)
# ─────────────────────────────────────────────
async def post_init(application: Application):
    asyncio.create_task(start_webserver(application))
    asyncio.create_task(keep_alive())

    try:
        await application.bot.send_message(
            chat_id=config.LOG_GROUP_ID,
            text="✅ Bot started successfully on Render 🚀"
        )
    except Exception:
        pass


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(post_init)   # ✅ CORRECT WAY
        .build()
    )

    # Commands
    application.add_handler(CommandHandler("approve", approve))
    application.add_handler(CommandHandler("verify", verify))
    application.add_handler(CommandHandler("badd", badd))
    application.add_handler(CommandHandler("bstick", bstick))

    # Callback buttons
    application.add_handler(
        CallbackQueryHandler(unverify_button, pattern="^unverify:")
    )

    # Bot added to group
    application.add_handler(
        ChatMemberHandler(on_bot_added, ChatMemberHandler.MY_CHAT_MEMBER)
    )

    # Moderation
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, monitor_text)
    )
    application.add_handler(
        MessageHandler(filters.Sticker.ALL, monitor_sticker)
    )
    application.add_handler(
        MessageHandler(filters.PHOTO, monitor_images)
    )

    print("🤖 Bot polling started...")
    application.run_polling()


if __name__ == "__main__":
    main()
