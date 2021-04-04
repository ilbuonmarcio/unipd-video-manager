from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from pprint import pprint
import dotenv
import json
import os

# loading credentials from UniPD
config = dotenv.dotenv_values(".env")

# setting chromedriver as headless to not fuck with us working!
options = Options()
options.add_argument('--headless')
options.add_argument("--log-level=3")
driver = webdriver.Chrome("./chromedriver.exe", chrome_options=options)

# logging into the elearning platform
driver.get("https://elearning.dei.unipd.it/mod/page/view.php?id=1673")
button = driver.find_element_by_css_selector('img[alt="Logo SSO Unipd"]')
button.click()
username = driver.find_element_by_id('j_username_js')
username.click()
username.clear()
username.send_keys(config['USERNAME'])
selector = driver.find_element_by_id('radio2')
selector.click()
password = driver.find_element_by_id('password')
password.click()
password.clear()
password.send_keys(config['PASSWORD'])
button = driver.find_element_by_id('login_button_js')
button.click()
# WE'RE IN!

courses_dict = {}

# obtaining courses list
courses = []
courses_blocks = driver.find_elements_by_css_selector('span.coursename a')
for course_block in courses_blocks:
    nome_corso = course_block.get_attribute('innerHTML').replace('<span class="accesshide "> Kaltura Video Resource</span>', '')
    course_link = course_block.get_attribute('href')
    
    course = [nome_corso, course_link]
    courses.append(course)

# parsing each course separately
for course in courses:
    print(f"Analizzando il corso: {course[0]}")
    driver.get(course[1])

    # finding all course videos
    videos_pages = driver.find_elements_by_css_selector('a[href^="https://elearning.dei.unipd.it/mod/kalvidres/view.php?id="]')

    nomi_video = []
    videos_pages_urls = []
    for i in range(0, len(videos_pages)):
        try:
            nome_video = videos_pages[i].find_element_by_class_name('instancename').get_attribute('innerHTML').replace('<span class="accesshide "> Kaltura Video Resource</span>', '')
            url_video = videos_pages[i].get_attribute('href')

            nomi_video.append(nome_video)
            videos_pages_urls.append(url_video)
        except:
            pass # ignoring wrong video link and title formats

    courses_dict[course[0]] = {}
    for video_page_url in videos_pages_urls:
        print(f"Grabbing video at url: {video_page_url}")
        driver.get(video_page_url)

        # getting iframe wrapper of the video
        iframe_wrapper = driver.find_element_by_css_selector('iframe#contentframe')
        driver.switch_to.frame(iframe_wrapper)

        # getting inner iframe of the video
        iframe_inner = driver.find_element_by_css_selector('iframe#kplayer_ifp')
        driver.switch_to.frame(iframe_inner)

        # finally, find the right video! that nesting is a bitch to us using selenium!
        video_element = driver.find_element_by_css_selector('.persistentNativePlayer')

        video_src = video_element.get_attribute('src')
        
        courses_dict[course[0]][nomi_video[videos_pages_urls.index(video_page_url)]] = video_src

        driver.switch_to.default_content()


with open('manifests_urls.json', 'w') as output_file:
    output_file.write(json.dumps(courses_dict))

driver.close()
