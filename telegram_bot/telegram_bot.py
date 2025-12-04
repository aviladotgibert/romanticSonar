from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
#from bot_service.romantic_bot import RomanticBot
import requests
import os

#bot = RomanticBot(ollama_url="http://localhost:11434")

API_URL = os.getenv("BOT_API_URL", "http://bot_service:5000")

async def start(update: Update, context):
    await update.message.reply_text(
        " Hola mi amor, soy Sonar. ¿Cómo estás?"
    )

async def chat(update: Update, context):
    user_id = str(update.effective_user.id)
    message = update.message.text
    
    #response = bot.chat(user_id, message)
    #await update.message.reply_text(response)

    payload = {
        "user_id": user_id,
        "message": message
    }

    try:
        response = requests.post(f"{API_URL}/chat", json=payload)
        sonar_reply = response.json().get("response", "No pude responder, amor.")
    except Exception as e:
        sonar_reply = f"Ocurrió un error hablando contigo, amor: {e}"

    await update.message.reply_text(sonar_reply)


def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN no está definido en variables de entorno")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    
    print("🤖 Bot de Telegram iniciado")
    app.run_polling()

if __name__ == '__main__':
    main()