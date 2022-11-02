from telegram.constants import FileSizeLimit

import requests
import youtube_dl

import os
from urllib.parse import urlparse

from helpers import get_compressed_video, get_compressed_audio
from web_browser import get_tik_tok_video_src
from insta import download_post, download_story, InstaError

class DownloadError(Exception):
    pass

def tiktok_video(url):
    video_src = get_tik_tok_video_src(url)
    if video_src is None:
        raise DownloadError("error_broken_link")
    
    r = requests.get(video_src)
    if r.status_code != 200:
        raise DownloadError("error_downloading_video")
    video = r.content
    if len(video) > FileSizeLimit.FILESIZE_UPLOAD:
        compressed_video = get_compressed_video(video, FileSizeLimit.FILESIZE_UPLOAD*0.999)
        if compressed_video is None:
            raise DownloadError("error_compressing_video")
        video = compressed_video

    return video

def youtube_audio(url):
    audio = get_youtube_audio(url)

    if len(audio) > FileSizeLimit.FILESIZE_UPLOAD:
        compressed_audio = get_compressed_audio(audio, FileSizeLimit.FILESIZE_UPLOAD*0.999)
        if compressed_audio is None:
            raise DownloadError("error_compressing_audio")
        audio = compressed_audio
    
    return audio

def get_youtube_audio(url):
    audio_file = "audio.mp3"
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

def instagram_video(url):
    url_path = urlparse(url).path
    path_parts = url_path[1:-1].split("/")
    path_type = path_parts[0]

    if path_type == "p":
        short_code = path_parts
        try:
            video = download_post(short_code)
        except InstaError as e:
            if str(e) == "fetching_video_failed":
                raise DownloadError("maybe_broken_link")
            elif str(e) == "post_is_not_video":
                raise DownloadError("instagram_post_is_not_video")
        return video
    elif path_type == "stories":
        username = path_parts[1]
        story_media_id = int(path_parts[2])
        try:
            video = download_story(username, story_media_id)
        except InstaError as e:
            if str(e) == "wrong_story_url":
                raise DownloadError("maybe_broken_link")
            elif str(e) == "story_is_not_video":
                raise DownloadError("instagram_story_is_not_video")
        return video
    


if __name__ == "__main__":
    url = "https://www.instagram.com/p/CkXqCicD0vixvzNqEHB0paPXzfV7Cu8wlKonOI0/"
    instagram_video(url)