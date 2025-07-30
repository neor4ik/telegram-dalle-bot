> neora:
import logging
import os
import sqlite3
import openai
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Логи
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Конфигурация токенов и ключей из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Настройки тарифов
TARIFFS = {
    "free": {"name": "Бесплатный", "tokens": 10, "price": "0 ₽"},
    "basic": {"name": "Базовый", "tokens": 50, "price": "120 ₽"},
    "optimal": {"name": "Оптимальный", "tokens": 150, "price": "400 ₽"},
    "premium": {"name": "Премиум", "tokens": 400, "price": "1000 ₽"},
}

TOKEN_COST = 3  # токенов за генерацию

# Инициализация базы SQLite
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    tokens INTEGER DEFAULT 0
)
"""
)
conn.commit()


def get_tokens(user_id: int) -> int:
    cursor.execute("SELECT tokens FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0


def set_tokens(user_id: int, tokens: int):
    if get_tokens(user_id) == 0:
        cursor.execute(
            "INSERT OR IGNORE INTO users(user_id, tokens) VALUES (?, ?)", (user_id, tokens)
        )
    else:
        cursor.execute("UPDATE users SET tokens = ? WHERE user_id = ?", (tokens, user_id))
    conn.commit()


def add_tokens(user_id: int, amount: int):
    current = get_tokens(user_id)
    set_tokens(user_id, current + amount)


# Клавиатура быстрых команд с иконками
quick_commands_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("🎨 Сгенерировать"), KeyboardButton("💰 Баланс")],
        [KeyboardButton("🛒 Купить"), KeyboardButton("📃 Тарифы")],
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
)


# Команды

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(f"{v['name']} — {v['price']}", callback_data=f"tariff_{k}")]
        for k, v in TARIFFS.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Добро пожаловать! Выберите тариф для получения токенов:", reply_markup=reply_markup
    )
    # Отправляем меню быстрых команд сразу после приветствия
    await update.message.reply_text(
        "Используйте меню ниже для быстрого доступа к командам.",
        reply_markup=quick_commands_keyboard,
    )


async def tariff_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected = query.data.split("_")[1]
    tariff = TARIFFS.get(selected)
    if not tariff:
        await query.edit_message_text("Неизвестный тариф.")
        return

    user_id = query.from_user.id
    add_tokens(user_id, tariff["tokens"])

    await query.edit_message_text(
        f"Вы выбрали тариф: {tariff['name']}\n"
        f"Вам начислено {tariff['tokens']} токенов.\n"
        f"Цена: {tariff['price']}\n\n"
        f"Стоимость одной генерации: {TOKEN_COST} токенов.\n"
        f"Используйте меню ниже для быстрого доступа к командам.",
        reply_markup=quick_commands_keyboard,
    )


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    tokens = get_tokens(user_id)
    await update.message.reply_text(f"У вас {tokens} токенов.", reply_markup=quick_commands_keyboard)


async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    tokens = get_tokens(user_id)
    if tokens < TOKEN_COST:
        await update.message.reply_text(
            f"Недостаточно токенов для генерации.\n"
            f"Купите тариф командой /start",
            reply_markup=quick_commands_keyboard,
        )
        return

    prompt = update.message.text
    if prompt == "🎨 Сгенерировать":
        await update.message.reply_text("Пожалуйста, отправьте описание для генерации изображения.")
        return

    # Если текст — это описание, то генерируем
    if prompt.strip() == "" or prompt in ["💰 Баланс", "🛒 Купить", "📃 Тарифы"]:
        # Игнорируем если это команда меню
        return

    set_tokens(user_id, tokens - TOKEN_COST)

    await update.message.reply_text("Генерирую изображение, подожди немного... 🎨")

    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512",
        )
        image_url = response["data"][0]["url"]
        await update.message.reply_photo(photo=image_url, caption="Готово ✅", reply_markup=quick_commands_keyboard)
    except Exception as e:
        logging.error(f"Ошибка OpenAI: {e}")
        await update.message.reply_text("❌ Произошла ошибка при генерации изображения.", reply_markup=quick_commands_keyboard)


async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Покупка токенов пока не реализована.\nСкоро добавим оплату через ЮMoney.", reply_markup=quick_commands_keyboard
    )


# Обработка меню быстрых сообщений
async def quick_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🎨 Сгенерировать":
        await update.message.reply_text("Пришлите описание для генерации изображения.")
    elif text == "💰 Баланс":
        await balance(update, context)
    elif text == "🛒 Купить":
        await buy(update, context)
    elif text == "📃 Тарифы":
        await start(update, context)


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(tariff_button, pattern=r"^tariff_"))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("buy", buy))

    from telegram.ext import MessageHandler

    # Обработка сообщений из меню быстрых сообщений
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), quick_command_handler))

    # Обработка текстовых сообщений для генерации после команды "🎨 Сгенерировать"
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), generate))

    print("Бот запущен...")
    app.run_polling()


if name == "__main__":
    main()


