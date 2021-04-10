from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from requests import get
from pprint import pprint
import dotenv
import shutil
import json
import os
import re

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

if not len(courses) > 0:
    print("Errore elenco corsi")
    exit(-1)

# parsing each course separately
for course in courses:
    print(f'{courses.index(course)+1}. -> {course[0]}')

# choose which course downlaod
course_selected = int(input("Seleziona il corso da scaricare: ")) - 1
try:
    course = courses[course_selected]
except:
    print("Corso non disponibile, idiota! Ma sai contare?")
    exit(-1)

print(f"Analizzando il corso: {course[0]}")

# se trova manifests_url.json già pronto per il corso scelto, salta
if os.path.isfile(f'manifests_urls.json'):
    print(f"manifests_urls.json giá presente, verifico l'esistenza del corso scelto...")
    with open("manifests_urls.json", 'r') as input_file:
        videos_string = "".join(input_file.readlines())
        videos = json.loads(videos_string)
        courses = list(videos.keys())
        if courses[0] == course[0]:
            print("Corso già scelto, passo al download...")
        else:
            download()
else:
    download()

# downloading videos
videos = None
with open("manifests_urls.json", 'r') as input_file:
    videos_string = "".join(input_file.readlines())
    videos = json.loads(videos_string)

courses = list(videos.keys())

course_name = courses[0]
videos = videos[course_name]

# sanitizing video courses
course_name = re.sub('[^\w\-_\.]', '_', course_name)

print(f'Corso selezionato: {course_name}, numero video disponibili: {len(videos)}')

video_download_id=1
for video_name, url_for_manifest in videos.items():
    print(f"Video {video_download_id}/{len(videos)}")
    # sanitizing video names
    video_name = re.sub('[^\w\-_\.]', '_', video_name)

    if os.path.isfile(f'export/{course_name}/{video_name}.mp4'):
        print(f"Video {video_name}.mp4 giá scaricato, passo al prossimo...")
        video_download_id += 1
        continue

    os.makedirs(f'./videos/', exist_ok=True)
    
    # downloading manifest file for different resolution urls
    response = get(url_for_manifest)
    if response.status_code != 200 or len(response.content) == 0:
        print("Error during manifest download, aborting")
        exit(-1)

    # getting best quality possible
    content = response.content.decode('utf-8')
    url_for_tokens = [row for row in content.split("\n") if len(row) > 0][-1]
    
    # downloading all tokens urls
    response = get(url_for_tokens)
    if response.status_code != 200 or len(response.content) == 0:
        print("Error during token urls descriptions download, aborting")
        exit(-1)
    
    # parsing all token urls
    content = response.content.decode('utf-8')
    tokens_urls = [row for row in content.split("\n") if len(row) > 0 and row[:5] == 'https']
    
    token_id = 0
    for url in tokens_urls:
        print(f"Downloading token id {str(token_id).zfill(4)}/{len(tokens_urls)}")
        with open(f'./videos/{str(token_id).zfill(4)}.mp4', "wb") as file:
            response = get(url)
            if response.status_code != 200 or len(response.content) == 0:
                print("Error during token url download, aborting")
                exit(-1)
            file.write(response.content)
        token_id += 1

    # concatenating all downloaded files
    video_tokens = os.listdir(f'./videos/')
    video_tokens = [video for video in video_tokens if video]
    with open('files.txt', 'w') as output_file:
        output_file.write("\n".join([f"file 'videos/{token}'" for token in video_tokens]))

    os.makedirs(f'./export/{course_name}/', exist_ok=True)
    os.system(f"ffmpeg -f concat -safe 0 -i files.txt -c copy export/{course_name}/{video_name}.mp4")

    # deleting tokens from disk
    shutil.rmtree(f'./videos/')

    # deleting files.txt file for ffmpeg
    if os.path.exists("files.txt"):
        os.remove("files.txt")

    video_download_id += 1



def download():
    driver.get(course[1])

                # finding all course videos
                videos_pages = driver.find_elements_by_css_selector('a[href^="https://elearning.dei.unipd.it/mod/kalvidres/view.php?id="]')
                print(f"Trovati {len(videos_pages)} video")

                nomi_video = []
                videos_pages_urls = []
                for i in range(0, len(videos_pages)):
                    try:
                        nome_video = videos_pages[i].find_element_by_class_name('instancename').get_attribute('innerHTML').replace('<span class="accesshide "> Kaltura Video Resource</span>', '')
                        url_video = videos_pages[i].get_attribute('href')

                        nomi_video.append(nome_video)
                        videos_pages_urls.append(url_video)
                    except:
                        pass #ignoring wrong video link and title formats

                name_video_id = 0
                courses_dict[course[0]] = {}
                for video_page_url in videos_pages_urls:
                    print(f"Grabbing {nomi_video[name_video_id]} at url: {video_page_url}")
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

                    name_video_id += 1

                with open('manifests_urls.json', 'w') as output_file:
                    output_file.write(json.dumps(courses_dict))

                driver.close()