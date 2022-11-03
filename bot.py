import os
import logging
from textwrap import dedent

from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, MessageHandler, filters

from dotenv import load_dotenv
from translation import translate as _
from helpers import is_url, get_url_path_parts
import download

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

async def message_handler(update: Update, context: CallbackContext):
    lang = "ru" if update.effective_user.language_code == "ru" else "en"

    if "highlight_id" in context.user_data:
        incoming_msg = update.message.text.strip()
        error_msg = None
        if incoming_msg.startswith("https://instagram.com"):
            path_parts = get_url_path_parts(incoming_msg)
            if len(path_parts) > 1:
                error_msg = _("incorrect_profile_url", lang)
            username = path_parts[0]
        elif len(incoming_msg.split(" ")) != 1:
            error_msg = _("incorrect_profile", lang)
        else:
            username = incoming_msg
        
        if error_msg is not None:
            await update.message.reply_text(error_msg)
        else:
            custom_url = f"https://www.instagram.com/highlights/{username}/{context.user_data['highlight_id']}"
            del context.user_data["highlight_id"]
            await social_network_url_handler(update, context, custom_url)
    else:
        await social_network_url_handler(update, context)

async def social_network_url_handler(update: Update, context: CallbackContext, custom_url: str = None):
    lang = "ru" if update.effective_user.language_code == "ru" else "en"
    url = update.message.text.strip() if custom_url is None else custom_url
    
    wrong_url_message = f"""
        {_("wrong_url_format", lang)}
        {_("bot_can_download", lang)}:
        1. <a href="https://www.tiktok.com/">TikTok</a>
        2. <a href="https://www.youtube.com/">YouTube</a>
        3. <a href="https://www.instagram.com/">Instagram</a>
    """

    if not is_url(url):
        await update.message.reply_text(dedent(wrong_url_message), parse_mode="HTML")
    elif url.startswith("https://www.tiktok.com"):
        wait_msg = await update.message.reply_text(_("wait", lang) + "...")
        try:
            video = download.tiktok_video(url)
        except download.DownloadError as e:
            await wait_msg.delete()
            await update.message.reply_text(_(str(e), lang))
            return

        await update.message.reply_video(video, read_timeout=50000, write_timeout=50000)
        await wait_msg.delete()
    elif url.startswith("https://www.youtube.com"):
        if "playlist" in url:
            await update.message.reply_text(_("no_youtube_playlist_accepted", lang) + "...")
            return
        
        wait_msg = await update.message.reply_text(_("wait", lang) + "...")
        try:
            audio = download.youtube_audio(url)
        except download.DownloadError as e:
            await wait_msg.delete()
            await update.message.reply_text(_(str(e), lang))
            return

        await update.message.reply_audio(audio, read_timeout=50000, write_timeout=50000)
        await wait_msg.delete()
    elif url.startswith("https://www.instagram.com"):
        wait_msg = await update.message.reply_text(_("wait", lang) + "...")
        try:
            result = download.instagram_video(url)
            if isinstance(result, str):
                highlight_id = result
                await wait_msg.delete()
                await request_author(update, context, highlight_id)
                return
            else:
                video = result
            
        except download.DownloadError as e:
            await wait_msg.delete()
            await update.message.reply_text(_(str(e), lang))
            return

        await update.message.reply_video(video, read_timeout=50000, write_timeout=50000)
        await wait_msg.delete()
    else:
        await update.message.reply_text(dedent(wrong_url_message), parse_mode="HTML")
    
async def request_author(update, context, highlight_id):
    lang = "ru" if update.effective_user.language_code == "ru" else "en"
    context.user_data["highlight_id"] = highlight_id

    await update.message.reply_text(_("need_to_get_profile", lang))

if __name__ == "__main__":
    app = ApplicationBuilder().token(os.environ.get("TELEGRAM_API_TOKEN")).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, message_handler))

    app.run_polling()