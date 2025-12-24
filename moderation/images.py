import os
import asyncio
from nudenet import NudeDetector

from database import users
from database import is_group_verified
from config import OWNER_ID, DELETE_DELAY
from moderation.text import delete_later


# Initialize detector once
detector = NudeDetector()


async def monitor_images(update, context):
    msg = update.message
    if not msg or not msg.photo:
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

    # ✅ Approved users bypass
    if users.find_one({"user_id": user.id, "approved": True}):
        return

    # Get highest resolution image
    photo = msg.photo[-1]
    file = await photo.get_file()

    path = f"/tmp/{photo.file_unique_id}.jpg"

    try:
        await file.download_to_drive(path)

        results = detector.detect(path)

        # 🔞 NSFW score check
        for r in results:
            if r.get("score", 0) >= 0.7:
                context.application.create_task(
                    delete_later(context, chat.id, msg.message_id)
                )
                break

    except Exception:
        # Silent fail (important for Render stability)
        pass

    finally:
        if os.path.exists(path):
            os.remove(path)
