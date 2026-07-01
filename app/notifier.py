from telegram import Bot
from app.config import BOT_TOKEN, CHAT_ID

bot = Bot(token=BOT_TOKEN)

def send_alert(message):
    try:
        bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")
