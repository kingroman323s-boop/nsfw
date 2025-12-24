from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client.tgmod

users = db.users
badwords = db.badwords
stickers = db.stickers

verified_groups = db.verified_groups


def verify_group(chat_id: int):
    verified_groups.update_one(
        {"chat_id": chat_id},
        {"$set": {"chat_id": chat_id}},
        upsert=True
    )


def unverify_group(chat_id: int):
    verified_groups.delete_one({"chat_id": chat_id})


def is_group_verified(chat_id: int) -> bool:
    return verified_groups.find_one({"chat_id": chat_id}) is not None

