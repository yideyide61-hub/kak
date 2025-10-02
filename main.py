import logging
import os
from flask import Flask
app = Flask(__name__)
from telegram import Update
from telegram.ext import Application, ChatMemberHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 🔑 Bot owner ID
BOT_OWNER_ID = 7124683213  # <-- replace with your Telegram user ID
TOKEN = os.getenv("8466271055:AAHxdB308HL6kbB4tbm6egj_vXrzjj7zwv8")  # Load from environment variable

# Flask app
app = Flask(__name__)

# Telegram Application
application = Application.builder().token(TOKEN).build()

# === Handler to check who added bot ===
async def check_who_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = update.my_chat_member
    if member.new_chat_member.user.id == context.bot.id:
        chat_id = member.chat.id
        adder = member.from_user
        chat_title = member.chat.title if member.chat.title else "Private Chat"

        logger.info(f"Bot added to group: {chat_title} (id={chat_id})")
        logger.info(f"Added by: {adder.full_name} (id={adder.id}, username=@{adder.username})")

        if adder.id != BOT_OWNER_ID:
            logger.warning(f"❌ {adder.full_name} is NOT the owner. Leaving {chat_title}.")
            await context.bot.send_message(chat_id, "⚠️ Not my owner. Leaving group.")
            await context.bot.leave_chat(chat_id)
        else:
            logger.info(f"✅ Bot added by owner {adder.full_name}. Staying in {chat_title}.")
            await context.bot.send_message(chat_id, "✅ Bot added by my owner. Ready to work!")

# Add handler
application.add_handler(ChatMemberHandler(check_who_added, ChatMemberHandler.MY_CHAT_MEMBER))

# === Flask webhook ===
@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"

@app.route("/")
def home():
    return "Bot is running via Render 🚀"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

