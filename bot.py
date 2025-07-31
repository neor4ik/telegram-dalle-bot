import os
import logging
import tempfile
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from moviepy.editor import ImageClip, AudioFileClip
import asyncio

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Состояния пользователей
user_states = {}

WAITING_FOR_PHOTO = "waiting_for_photo"
WAITING_FOR_AUDIO = "waiting_for_audio"

# Клавиатура
quick_commands_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("🎬 Создать видео")],
        [KeyboardButton("🔁 Отменить")],
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
)

# Команда /start или "🎬 Создать видео"
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_states[user_id] = {
        "state": WAITING_FOR_PHOTO,
        "photo_path": None,
        "audio_paths": []
    }
    await update.message.reply_text(
        "📸 Пришли фото, которое будет использоваться как фон для видео.",
        reply_markup=quick_commands_keyboard
    )

# Фото
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = user_states.get(user_id)

    if not state or state["state"] != WAITING_FOR_PHOTO:
        await update.message.reply_text("Сначала нажми '🎬 Создать видео'")
        return

    photo_file = await update.message.photo[-1].get_file()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tf:
        await photo_file.download_to_drive(custom_path=tf.name)
        state["photo_path"] = tf.name

    state["state"] = WAITING_FOR_AUDIO
    await update.message.reply_text(
        "🎵 Фото получено! Теперь отправь один или несколько аудиофайлов. Когда всё будет готово, напиши /done."
    )

# Аудио
async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = user_states.get(user_id)

    if not state or state["state"] != WAITING_FOR_AUDIO:
        await update.message.reply_text("Сначала отправь фото.")
        return

    audio = update.message.audio or update.message.voice
    if not audio:
        await update.message.reply_text("Пожалуйста, отправь аудио (mp3/voice).")
        return

    audio_file = await audio.get_file()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tf:
        await audio_file.download_to_drive(custom_path=tf.name)
        state["audio_paths"].append(tf.name)

    await update.message.reply_text("✅ Аудио принято. Можешь отправить ещё или /done для генерации.")

# /done — генерация
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = user_states.get(user_id)

    if not state or state["state"] != WAITING_FOR_AUDIO:
        await update.message.reply_text("Нет активной сессии. Нажми «🎬 Создать видео».")
        return

    if not state["photo_path"] or not state["audio_paths"]:
        await update.message.reply_text("Недостаточно данных. Нужно фото и хотя бы один аудиофайл.")
        return

    await update.message.reply_text("🎥 Генерирую видео...")

    videos = []
    try:
        for i, audio_path in enumerate(state["audio_paths"], start=1):
            video_path = await asyncio.to_thread(
                generate_video,
                state["photo_path"],
                audio_path,
                f"video_{user_id}_{i}.mp4"
            )
            videos.append(video_path)

        for video_file in videos:
            with open(video_file, "rb") as f:
                await update.message.reply_video(video=f)
    except Exception as e:
        logging.error(f"Ошибка генерации видео: {e}")
        await update.message.reply_text("❌ Ошибка при генерации видео.")
    finally:
        cleanup_files([state["photo_path"]] + state["audio_paths"] + videos)
        user_states.pop(user_id,
OLXTOTO: Link Alternatif Login Togel Online & Taruhan angka Terpercaya
OLXTOTO: Link Alternatif Login Togel Online & Taruhan angka Terpercaya
furyevents.co.uk


ne)

# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_states.pop(user_id, None)
    await update.message.reply_text("❌ Сессия отменена.", reply_markup=quick_commands_keyboard)

# Быстрые кнопки
async def handle_quick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🎬 Создать видео":
        await start(update, context)
    elif text == "🔁 Отменить":
        await cancel(update, context)

# Генерация видео
def generate_video(photo_path, audio_path, output_path):
    audio_clip = AudioFileClip(audio_path)
    image_clip = ImageClip(photo_path).set_duration(audio_clip.duration).set_audio(audio_clip)
    image_clip.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", verbose=False, logger=None)
    return output_path

# Очистка
def cleanup_files(files):
    for f in files:
        try:
            os.remove(f)
        except Exception:
            pass

# main
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("done", done))
    app.add_handler(CommandHandler("cancel", cancel))

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_quick_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.AUDIO | filters.VOICE, handle_audio))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main() No

if __name__ == "__main__":
    main()


