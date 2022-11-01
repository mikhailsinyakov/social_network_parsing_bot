from telegram.constants import FileSizeLimit

import requests
import youtube_dl
import os

from helpers import get_compressed_video, get_compressed_audio
from web_browser import get_tik_tok_video_src

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

if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=a5myHuC"
    youtube_audio(url)