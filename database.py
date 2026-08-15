from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["personal_bot"]

# Do collections:
# messages -> forwarded message ko user se link karta hai
# users    -> saare users ki list (broadcast/stats ke liye)
messages = db["messages"]
users = db["users"]


def save_message_link(forwarded_msg_id, user_id):
    messages.update_one(
        {"forwarded_msg_id": forwarded_msg_id},
        {"$set": {"user_id": user_id}},
        upsert=True,
    )


def get_user_from_message(forwarded_msg_id):
    doc = messages.find_one({"forwarded_msg_id": forwarded_msg_id})
    return doc["user_id"] if doc else None


def save_user(user_id, first_name, username):
    users.update_one(
        {"user_id": user_id},
        {"$set": {"first_name": first_name, "username": username}},
        upsert=True,
    )


def get_all_users():
    return [u["user_id"] for u in users.find({}, {"user_id": 1})]


def count_users():
    return users.count_documents({})
