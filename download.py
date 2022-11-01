from telegram.constants import FileSizeLimit

import requests

from helpers import get_compressed_video
from web_brower import get_tik_tok_video_src

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


if __name__ == "__main__":
    url = "https://www.tiktok.com/@qazaqsamat/video/7159162035031346437?is_copy_url=1&is_from_webapp=v1"
    tiktok_video(url)