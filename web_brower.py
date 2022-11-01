from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def get_webdriver():
    chrome_options = Options()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)
    return driver

def get_tik_tok_video_src(url):
    driver = get_webdriver()
    driver.get(url)
    try:
        video_elements = driver.find_elements(By.TAG_NAME, "video")
        if len(video_elements) != 1:
            return None
        video_element = driver.find_element(By.TAG_NAME, "video")
    except NoSuchElementException:
        return None
    video_src = video_element.get_attribute("src")

    return video_src