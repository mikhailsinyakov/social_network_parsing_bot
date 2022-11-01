from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from telegram.constants import FileSizeLimit

import requests
import os

from helpers import get_compressed_video

def get_webdriver():
    chrome_options = Options()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)
    return driver

def tiktok_video(url):
    driver = get_webdriver()
    driver.get(url)
    video_element = driver.find_element(By.TAG_NAME, "video")
    video_src = video_element.get_attribute("src")
    
    r = requests.get(video_src)
    if r.status_code != 200:
        return None
    video = r.content
    if len(video) > FileSizeLimit.FILESIZE_UPLOAD:
        compressed_video = get_compressed_video(video, FileSizeLimit.FILESIZE_UPLOAD*0.999)
        if compressed_video is None:
            return None
        video = compressed_video

    return video
  

if __name__ == "__main__":
    url = "https://www.tiktok.com/@qazaqsamat/video/7159162035031346437?is_copy_url=1&is_from_webapp=v1"
    tiktok_video(url)