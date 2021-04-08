from pprint import pprint
from requests import get
import shutil
import re
import json
import os

def download():
    videos = None
    with open("manifests_urls.json", 'r') as input_file:
        videos_string = "".join(input_file.readlines())
        videos = json.loads(videos_string)

    courses = list(videos.keys())
    for course in courses:
        print(f'{courses.index(course)+1}. -> {course}')

    course_selected = int(input("Seleziona il corso da scaricare: ")) - 1
    try:
        course_name = courses[course_selected]
    except:
        print("Corso non disponibile, idiota! Ma sai contare?")
        exit(-1)
    
    videos = videos[course_name]

    # sanitizing video courses
    course_name = re.sub('[^\w\-_\.]', '_', course_name)

    print(f'Corso selezionato: {course_name}, numero video disponibili: {len(videos)}')

    for video_name, url_for_manifest in videos.items():
        # sanitizing video names
        video_name = re.sub('[^\w\-_\.]', '_', video_name)

        if os.path.isfile(f'export/{course_name}/{video_name}.mp4'):
            print(f"Video {video_name}.mp4 giá scaricato, passo al prossimo...")
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
            print(f"Downloading token id {str(token_id).zfill(4)}")
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


if __name__ == "__main__":
    download()