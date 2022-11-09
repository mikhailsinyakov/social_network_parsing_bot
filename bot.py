import os
import logging
from textwrap import dedent

from dotenv import load_dotenv

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, MessageHandler, filters, PicklePersistence, CallbackQueryHandler

from translation import translate as _
from helpers import is_url, get_url_path_parts, build_history_item, get_history_stats
import download
from processes import execute_in_another_process

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
        if incoming_msg.startswith("https://instagram.com") or incoming_msg.startswith("https://www.instagram.com"):
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
    msg = update.message.text.strip()
    user_id = update.message.from_user.id

    if "history" not in context.bot_data:
        context.bot_data["history"] = []

    if custom_url is not None:
        url = custom_url
    else:
        start = msg.find("https://")
        if start != -1:
            end = msg.index(" ", start) if " " in msg[start:] else len(msg)
            url = msg[start:end]
        else:
            url = msg

    if "request_is_processing" in context.user_data:
        await update.message.reply_text(_("have_unprocessed_request", lang))
    elif not is_url(url):
        await send_wrong_url_message(update, lang)
    elif url.startswith(("https://www.tiktok.com", "https://vt.tiktok.com")):
        wait_msg = await update.message.reply_text(_("wait", lang) + "...")
        context.user_data["request_is_processing"] = True
        try:
            video = await execute_in_another_process(download.tiktok_video, url, user_id)
        except download.DownloadError as e:
            await wait_msg.delete()
            await update.message.reply_text(_(str(e), lang))
            return
        finally:
            del context.user_data["request_is_processing"]

        context.bot_data["history"].append(build_history_item(user_id, "tiktok"))
        await update.message.reply_video(video, read_timeout=50000, write_timeout=50000)
        await wait_msg.delete()
    elif url.startswith(("https://www.youtube.com", "https://youtu.be")):
        if "playlist" in url:
            await update.message.reply_text(_("no_youtube_playlist_accepted", lang) + "...")
            return
        
        wait_msg = await update.message.reply_text(_("wait", lang) + "...")
        context.user_data["request_is_processing"] = True
        try:
            audio = await execute_in_another_process(download.youtube_audio, url, user_id)
        except download.DownloadError as e:
            await wait_msg.delete()
            await update.message.reply_text(_(str(e), lang))
            return
        finally:
            del context.user_data["request_is_processing"]

        context.bot_data["history"].append(build_history_item(user_id, "youtube"))
        await update.message.reply_audio(audio, read_timeout=50000, write_timeout=50000)
        await wait_msg.delete()
    elif url.startswith(("https://www.instagram.com", "https://instagram.com")):
        wait_msg = await update.message.reply_text(_("wait", lang) + "...")
        context.user_data["request_is_processing"] = True
        try:
            result = await execute_in_another_process(download.instagram_video, url, user_id)
            if isinstance(result, str):
                highlight_id = result
                await wait_msg.delete()
                await request_author(update, context, highlight_id)
                return
            else:
                video = result
        except download.DownloadError as e:
            if str(e) == "suspicious_activity":
                await context.bot.send_message(int(os.environ.get("ADMIN_ID")), str(e))
                await update.message.reply_text(_("fetching_video_failed", lang))
            else:
                await update.message.reply_text(_(str(e), lang))
            
            await wait_msg.delete()
            return
        finally:
            del context.user_data["request_is_processing"]
        
        context.bot_data["history"].append(build_history_item(user_id, "instagram"))
        await update.message.reply_video(video, read_timeout=50000, write_timeout=50000)
        await wait_msg.delete()
    else:
        await send_wrong_url_message(update, lang)
    
async def request_author(update, context, highlight_id):
    lang = "ru" if update.effective_user.language_code == "ru" else "en"
    context.user_data["highlight_id"] = highlight_id

    await update.message.reply_text(_("need_to_get_profile", lang))

async def send_wrong_url_message(update, lang):
    wrong_url_message = f"""
        {_("wrong_url_format", lang)}
        {_("bot_can_download", lang)}:
        1. <a href="https://www.tiktok.com/">TikTok</a>
        2. <a href="https://www.youtube.com/">YouTube</a>
        3. <a href="https://www.instagram.com/">Instagram</a>
    """
    await update.message.reply_text(dedent(wrong_url_message), parse_mode="HTML")

async def get_stats(update, context):
    lang = "ru" if update.effective_user.language_code == "ru" else "en"
    user_id = update.message.from_user.id

    if user_id != int(os.environ.get("ADMIN_ID")):
        await send_wrong_url_message(update, lang)
    else:
        btns = [InlineKeyboardButton(_(social_name, lang), callback_data=social_name) for social_name in ["tiktok", "youtube", "instagram"]]
        all_social_btn = InlineKeyboardButton(_("all_above", lang), callback_data="all_social")
        keyboard = InlineKeyboardMarkup([btns, [all_social_btn]])

        context.user_data["stats_filters"] = {
            "social_network": None,
            "interval": None
        }
        await update.message.reply_text(_("choose_social_network", lang) + ":", reply_markup=keyboard)

async def handle_callback_query(update, context):
    lang = "ru" if update.effective_user.language_code == "ru" else "en"
    query = update.callback_query
    await query.answer()

    if "stats_filters" in context.user_data:
        if context.user_data["stats_filters"]["social_network"] is None:
            context.user_data["stats_filters"]["social_network"] = query.data

            btns = [InlineKeyboardButton(_(social_name, lang), callback_data=social_name) for social_name in ["hour", "day", "week"]]
            all_time_btn = InlineKeyboardButton(_("all_time", lang), callback_data="all_time")
            keyboard = InlineKeyboardMarkup([btns, [all_time_btn]])

            await context.bot.send_message(chat_id=query.message.chat.id, text=_("choose_interval", lang) + ":", reply_markup=keyboard)
        elif context.user_data["stats_filters"]["interval"] is None:
            social_network = context.user_data["stats_filters"]["social_network"]
            interval = query.data

            del context.user_data["stats_filters"]

            if social_network == "all_social": social_network = None
            if interval == "all_time": interval = None
            n_requests = get_history_stats(context.bot_data.get("history", []), social_type=social_network, interval=interval)

            social_network_str = social_network if social_network is not None else _("all_social", lang).lower()
            interval_str = interval if interval is not None else _("all_time", lang).lower()
            msg = f"{_('n_requests', lang)} {social_network_str} for {interval_str}: {n_requests}"

            await context.bot.send_message(chat_id=query.message.chat.id, text=msg)


if __name__ == "__main__":
    my_persistence = PicklePersistence("data.pkl")
    app = ApplicationBuilder().token(os.environ.get("TELEGRAM_API_TOKEN")).persistence(my_persistence).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("get_stats", get_stats))
    app.add_handler(MessageHandler(filters.TEXT, message_handler, block=False))
    app.add_handler(CallbackQueryHandler(handle_callback_query))

    app.run_polling()