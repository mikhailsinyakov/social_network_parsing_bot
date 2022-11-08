from telegram.constants import FileSizeLimit

import requests
import youtube_dl

import os
import base64

from helpers import get_url_path_parts
from media_file_conversion import compress, ConversionError
from web_browser import get_tik_tok_video_src
from insta import download_post_or_reel, download_story, download_highlights, InstaError

class DownloadError(Exception):
    pass

def tiktok_video(url, user_id):
    video_src = get_tik_tok_video_src(url)
    if video_src is None:
        raise DownloadError("error_broken_link")
    
    r = requests.get(video_src)
    if r.status_code != 200:
        raise DownloadError("error_downloading_video")
    video = r.content
    if len(video) > FileSizeLimit.FILESIZE_UPLOAD:
        try:
            compressed_video = compress("video", video, FileSizeLimit.FILESIZE_UPLOAD*0.999, user_id)
        except ConversionError:
            raise DownloadError("error_compressing_video")
        video = compressed_video

    return video

def youtube_audio(url, user_id):
    audio = get_youtube_audio(url, user_id)

    if len(audio) > FileSizeLimit.FILESIZE_UPLOAD:
        try:
            compressed_audio = compress("audio", audio, FileSizeLimit.FILESIZE_UPLOAD*0.999, user_id)
        except ConversionError:
            raise DownloadError("error_compressing_audio")
        audio = compressed_audio
    
    return audio

def get_youtube_audio(url, user_id):
    audio_file = f"{user_id}_audio.mp3"
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "outtmpl": audio_file,
        "noplaylist": True
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except youtube_dl.utils.DownloadError:
            raise DownloadError("error_broken_link")
    
    with open(audio_file, "rb") as f:
        audio = f.read()
    
    os.remove(audio_file)
    return audio

def instagram_video(url, user_id):
    path_parts = get_url_path_parts(url)

    path_type = path_parts[0]
    if path_type in ["p", "reel"]:
        return get_instagram_video(path_type, user_id, {"short_code": path_parts[1]})
    elif path_type == "stories":
        if path_parts[1] == "highlights":
            return path_parts[2]
        return get_instagram_video(path_type, user_id, {"username": path_parts[1], "story_media_id": int(path_parts[2])})
    elif path_type == "highlights":
        return get_instagram_video(path_type, user_id, {"username": path_parts[1], "highlight_id": int(path_parts[2])})
    elif path_type == "s":
        encoded_text = path_parts[1]
        highlight_id = base64.b64decode(encoded_text).decode("utf-8").split(":")[1]
        return highlight_id


def get_instagram_video(type, user_id, kwargs):
    fn = download_post_or_reel if type in ["p", "reel"] else download_story if type == "stories" else download_highlights if type == "highlights" else None
    if fn is not None:
        try:
            video = fn(user_id, **kwargs)
        except InstaError as e:
            if str(e) == "accessing_private_profile":
                raise DownloadError("accessing_private_profile")
            elif str(e) == "fetching_video_failed":
                raise DownloadError("maybe_broken_link")
            elif str(e) == "obj_is_not_video":
                raise DownloadError("instagram_obj_is_not_video")
            elif str(e) == "wrong_story_url":
                raise DownloadError("maybe_broken_link")
            elif str(e) == "story_is_not_video":
                raise DownloadError("instagram_story_is_not_video")
            elif str(e) == "incorrect_profile_name":
                raise DownloadError("maybe_broken_link")
            elif str(e) == "no_video_highlights":
                raise DownloadError("no_video_highlights")
            elif str(e) == "concatting_videos_failed":
                raise DownloadError("error_concatting_videos")
            elif str(e) == "suspicious_activity":
                raise DownloadError(str(e))
    
    if len(video) > FileSizeLimit.FILESIZE_UPLOAD:
        try:
            compressed_video = compress("video", video, FileSizeLimit.FILESIZE_UPLOAD*0.999, user_id)
        except ConversionError:
            raise DownloadError("error_compressing_video")
        video = compressed_video
    
    return video



if __name__ == "__main__":
    url = "https://www.instagram.com/stories/highlights/17869943995235799/"
    print(instagram_video(url))