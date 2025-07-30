import logging
import os
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Логи
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Получаем токены из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Обработка команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Пришли мне описание, и я создам изображение ✨")

# Обработка текстовых сообщений — генерируем изображение
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    await update.message.reply_text("Генерирую изображение, подожди немного... 🎨")

    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        )
        image_url = response['data'][0]['url']
        await update.message.reply_photo(photo=image_url, caption="Готово ✅")
    except Exception as e:
        logging.error(f"Ошибка OpenAI: {e}")
        await update.message.reply_text("❌ Произошла ошибка при генерации изображения.")

# Основная функция запуска бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Бот запущен...")
    app.run_polling()
