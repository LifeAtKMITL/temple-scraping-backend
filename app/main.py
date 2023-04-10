from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import re

app = FastAPI()

origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:5174",
    "http://localhost:5174",
    "https://temple-scraping.zantaclaus.dev",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def fetch_data(url):
    response = requests.get(url)

    scraped_text = response.text

    # match div with class mw-parser-output to the line with the word "ดูเพิ่ม"
    pattern1 = r'^.*?<div class="mw-parser-output">((?:.*\n)*?)^.*?ดูเพิ่ม.*$'

    match = re.search(pattern1, scraped_text, re.MULTILINE)

    if match:
        container_content = match.group(1)

        # match the line that include <li> tag
        pattern2 = r'^.*<li>.*$'

        # all the lines that include <li> tag
        all_li_tags = re.findall(pattern2, container_content, re.MULTILINE)

        # get content inside tags <h1>content here<h2>some thing else</h2></h1> -> ["co r'(?<!<)(?![^<>]*>)[^<>]+(?<!>)'ntent here", "some thing else""]
        pattern3 = r'(?<!<)(?![^<>]*>)[^<>]+(?<!>)'
        match_temple = set()
        for tag in all_li_tags:

            # Find all matches
            matches = re.findall(pattern3, tag)

            temple_string_without_tambol = ' '.join(matches)

            pattern4 = r'^.*?(?= ตำ)'
            res = re.findall(pattern4, temple_string_without_tambol)

            # add space after the temple name (for the special case that after pattern 4 theres no space after the temple name)
            res[0] = res[0] + ' '

            pattern5 = r'^.*?(?= )'
            new_res = re.findall(pattern5, res[0])

            temple_clean = new_res[0]

            match_temple.add(temple_clean)

        print(url, len(match_temple))

        return match_temple
    else:
        return "No match found."


@app.get("/")
def read_root():
    base_url = 'https://th.wikipedia.org/wiki/รายชื่อวัดในจังหวัด'
    provinces = ['ราชบุรี', 'ลพบุรี', 'ลำปาง', 'ลำพูน']

    res = []
    for province in provinces:
        res.append(
            {'province': province, 'data': fetch_data(base_url + province)})

    return res


# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host="localhost", port=8000)
