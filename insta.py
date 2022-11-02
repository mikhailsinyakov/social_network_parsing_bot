import os

import instaloader
from dotenv import load_dotenv

from helpers import get_video_file_and_delete_folder

load_dotenv()

L = None

class InstaError(Exception):
    pass

def init_instaloader():
    global L
    L = instaloader.Instaloader()
    L.login(os.environ.get("INSTAGRAM_USERNAME"), os.environ.get("INSTAGRAM_PASSWORD"))

def download_post(post_short_code):
    global L
    if L is None:
        init_instaloader()
    
    download_folder = "post"
    
    try:
        post = instaloader.Post.from_shortcode(L.context, post_short_code)
    except instaloader.exceptions.BadResponseException:
        raise InstaError("fetching_video_failed")
    
    if not post.is_video:
        raise InstaError("post_is_not_video")
    L.download_post(post, download_folder)

    video = get_video_file_and_delete_folder(download_folder)
    if video is None:
        raise InstaError("post_is_not_video")
    
    return video


if __name__ == "__main__":
    video = download_post("CkXqCicD0vixvzNqEHB0paPXzfV7Cu8wlKonOI")

    with open("post_video.mp4", "wb") as f:
        f.write(video)