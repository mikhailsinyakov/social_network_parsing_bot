import os

import instaloader
from dotenv import load_dotenv

from helpers import get_video_file, delete_folder, get_video_names, concat_videos

load_dotenv()

L = None

class InstaError(Exception):
    pass

def init_instaloader():
    global L
    L = instaloader.Instaloader()
    L.login(os.environ.get("INSTAGRAM_USERNAME"), os.environ.get("INSTAGRAM_PASSWORD"))

def download_post_or_reel(short_code):
    global L
    if L is None:
        init_instaloader()
    
    download_folder = "obj"
    
    try:
        obj = instaloader.Post.from_shortcode(L.context, short_code)
    except instaloader.exceptions.BadResponseException:
        raise InstaError("fetching_video_failed")
    
    if not obj.is_video:
        raise InstaError("obj_is_not_video")
    L.download_post(obj, download_folder)

    video = get_video_file(download_folder)
    delete_folder(download_folder)
    if video is None:
        raise InstaError("obj_is_not_video")
    
    return video

def download_story(username, story_media_id):
    global L
    if L is None:
        init_instaloader()
    
    download_folder = "story"
    
    try:
        profile = L.check_profile_id(username)
    except instaloader.exceptions.ProfileNotExistsException:
        raise InstaError("wrong_story_url")
    userid = profile.userid
    stories = L.get_stories([userid])

    story_items = [item for story in stories for item in story.get_items() if item.mediaid == story_media_id]

    if not story_items:
        delete_folder(username)
        raise InstaError("wrong_story_url")
    
    story_item = story_items[0]

    if not story_item.is_video:
        delete_folder(username)
        raise InstaError("story_is_not_video")
    
    L.download_storyitem(story_item, download_folder)

    video = get_video_file(download_folder)
    delete_folder(download_folder)

    if video is None:
        raise InstaError("story_is_not_video")
    
    delete_folder(username)
    
    return video

def download_highlights(username, highlight_id):
    global L
    if L is None:
        init_instaloader()
    
    download_folder = "highlights"

    try:
        profile = L.check_profile_id(username)
    except instaloader.exceptions.ProfileNotExistsException:
        raise InstaError("incorrect_profile_name")
    userid = profile.userid
    highlights = L.get_highlights(userid)
    
    story_items = [item for highlight in highlights if highlight.unique_id == highlight_id for item in highlight.get_items() if item.is_video]
    if not story_items:
        raise InstaError("no_video_highlights")

    for item in story_items:
        L.download_storyitem(item, download_folder)
    
    output_video_name = "video.mp4"

    concat_videos(download_folder, get_video_names(download_folder), output_video_name)

    delete_folder(download_folder)
    delete_folder(username)

    try:
        with open(output_video_name, "rb") as f:
            video = f.read()
    except FileNotFoundError:
        raise InstaError("concatting_videos_failed")
    
    os.remove(output_video_name)

    return video

if __name__ == "__main__":
    video = download_highlights("anne.abubakar", 17869943995235799)
    print(len(video))
