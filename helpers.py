import validators
from validators import ValidationFailure

import os
import shutil
from urllib.parse import urlparse
from datetime import datetime, timedelta

def is_url(s):
    result = validators.url(s)

    if isinstance(result, ValidationFailure):
        return False

    return result

def get_video_file(folder_name):
    video_file_names = [filename for filename in os.listdir(folder_name) if os.path.splitext(filename)[1] in [".mov", ".mp4", ".gif"]]
    if not video_file_names:
        return None
    video_file_name = video_file_names[0]

    with open(folder_name + "/" + video_file_name, "rb") as f:
        video = f.read()

    return video

def delete_folder(folder_name):
    shutil.rmtree(folder_name)

def get_video_names(folder_name):
    print(os.listdir(folder_name))
    return [filename for filename in os.listdir(folder_name) if os.path.splitext(filename)[1] == ".mp4"]

def get_url_path_parts(url):
    url_path = urlparse(url).path
    return url_path[1:].split("/")

def build_history_item(user_id, social_type):
    return {"time": datetime.now(), "user_id": user_id, "social_type": social_type}

def get_history_stats(_history, social_type=None, interval=None):
    history = _history.copy()
    if social_type is not None:
        history = [item for item in history if item["social_type"] == social_type]
    if interval is not None:
        now = datetime.now()
        hours = interval["hours"] if "hours" in interval else 0
        days = interval["days"] if "days" in interval else 0
        duration = timedelta(days=days, hours=hours)
        history = [item for item in history if (now - item["time"]) < duration]
    
    return len(history)