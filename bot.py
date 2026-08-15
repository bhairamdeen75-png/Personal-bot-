import telebot
from flask import Flask, request, abort

import config
import database as db

bot = telebot.TeleBot(config.BOT_TOKEN)
app = Flask(__name__)


# ---------- USER SIDE ----------

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id == config.OWNER_ID:
        bot.reply_to(message, "Bot ready hai! Users ke messages yahan aayenge. Reply karne ke liye us message par 'Reply' karke apna jawab likhein.")
    else:
        db.save_user(message.chat.id, message.from_user.first_name, message.from_user.username)
        bot.reply_to(message, "Namaste! Apna message bhejein, main jaldi hi jawab dunga.")


@bot.message_handler(
    func=lambda m: m.chat.id != config.OWNER_ID,
    content_types=['text', 'photo', 'video', 'document', 'sticker', 'voice', 'audio']
)
def handle_user(message):
    db.save_user(message.chat.id, message.from_user.first_name, message.from_user.username)
    # User ka message owner ko forward karo
    fwd = bot.forward_message(config.OWNER_ID, message.chat.id, message.message_id)
    # Link save karo taaki reply wapas ja sake
    db.save_message_link(fwd.message_id, message.chat.id)


# ---------- OWNER SIDE ----------

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.chat.id != config.OWNER_ID:
        return
    bot.reply_to(message, f"Total users: {db.count_users()}")


@bot.message_handler(
    func=lambda m: m.chat.id == config.OWNER_ID and m.reply_to_message is not None,
    content_types=['text', 'photo', 'video', 'document', 'sticker', 'voice', 'audio']
)
def handle_owner_reply(message):
    target_user = db.get_user_from_message(message.reply_to_message.message_id)
    if target_user is None:
        bot.reply_to(message, "Is message ka user nahi mila.")
        return
    # Owner ka reply user ko bhejo (copy_message se aapki identity chhupi rehti hai)
    bot.copy_message(target_user, config.OWNER_ID, message.message_id)


# ---------- WEBHOOK ROUTES ----------

@app.route('/' + config.BOT_TOKEN, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        bot.process_new_updates([update])
        return '', 200
    abort(403)


@app.route('/', methods=['GET'])
def index():
    # UptimeRobot yahan ping karega taaki service sleep na ho
    return "Bot is running!", 200


@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=config.WEBHOOK_URL + '/' + config.BOT_TOKEN)
    return "Webhook set!", 200


if __name__ == '__main__':
    # Startup par webhook set karo
    bot.remove_webhook()
    if config.WEBHOOK_URL:
        bot.set_webhook(url=config.WEBHOOK_URL + '/' + config.BOT_TOKEN)
    app.run(host='0.0.0.0', port=config.PORT)
