import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import openai
import requests

openai.api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Пришли описание — сгенерирую картинку.")

async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    await update.message.reply_text("Генерация…")
    try:
        resp = openai.Image.create(prompt=prompt, n=1, size="512x512")
        url = resp['data'][0]['url']
        img_data = requests.get(url).content
        await update.message.reply_photo(photo=img_data)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

if name == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), generate_image))
    print("Бот запущен")
    app.run_polling()
