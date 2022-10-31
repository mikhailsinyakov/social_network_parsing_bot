import os
import logging
from textwrap import dedent

from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler

from dotenv import load_dotenv
from translation import translate as _

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

load_dotenv()

async def start(update: Update, context: CallbackContext):
    lang = "ru" if update.effective_user.language_code == "ru" else "en"
    
    msg = f"""
    <b>{_("greeting", lang)}!</b> {_("how_to_use_bot", lang)}
    1. {_("go_to_social_network", lang)}.
    2. {_("choose_video", lang)}.
    3. {_("click_copy_button", lang)}.
    4. {_("send_to_bot", lang)}!

    {_("bot_can_download", lang)}:
    1. <a href="https://www.tiktok.com/">TikTok</a> ({_("without_watermark", lang)})
    2. <a href="https://www.youtube.com/">YouTube</a> ({_("only_sound", lang)})
    3. <a href="https://www.instagram.com/">Instagram</a> ({_("instagram_options", lang)})
    """

    await update.message.reply_text(dedent(msg), parse_mode="HTML")

if __name__ == "__main__":
    app = ApplicationBuilder().token(os.environ.get("TELEGRAM_API_TOKEN")).build()

    app.add_handler(CommandHandler("start", start))

    app.run_polling()