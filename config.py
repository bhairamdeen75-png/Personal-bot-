import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID"))
MONGO_URI = os.environ.get("MONGO_URI")

# Webhook ke liye - deploy hone ke baad platform ka URL yahan aayega
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # e.g. https://your-app.koyeb.app
PORT = int(os.environ.get("PORT", 8080))
