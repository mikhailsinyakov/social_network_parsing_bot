import validators
from validators import ValidationFailure

import os
import shutil
from urllib.parse import urlparse

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

