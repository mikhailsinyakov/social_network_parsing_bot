import os
import logging
from textwrap import dedent

from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler

from dotenv import load_dotenv

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

load_dotenv()

async def start(update: Update, context: CallbackContext):
    msg = """
    <b>Приветствую!</b> Ниже я расскажу вам как пользоваться ботом!
    1. Зайдите в одну из социальных сетей.
    2. Выберите интересное для вас видео.
    3. Нажми кнопку "Скопировать".
    4. Отправьте нашему боту и получите ваш файл!

    Бот может скачивать с:
    1. <a href="https://www.tiktok.com/">TikTok</a> (без водяного знака)
    2. <a href="https://www.youtube.com/">YouTube</a> (только звук)
    3. <a href="https://www.instagram.com/">Instagram</a> (посты, истории, reels, хайлайты)
    """

    await update.message.reply_text(dedent(msg), parse_mode="HTML")

if __name__ == "__main__":
    app = ApplicationBuilder().token(os.environ.get("TELEGRAM_API_TOKEN")).build()

    app.add_handler(CommandHandler("start", start))

    app.run_polling()