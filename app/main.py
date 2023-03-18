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
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def fetch_data(url):
    def filter_strings(strings, pattern):
        regex = re.compile(pattern)
        return list(filter(regex.match, strings))

    # request the webpage
    response = requests.get(url)
    html = response.content.decode('utf-8')

    # read content in div with id='mw-content-text'
    pattern = r'<div\s+[^>]*id\s*=\s*[\'"]mw-content-text[\'"][^>]*>(.*?)<\/div>'
    match = re.search(pattern, html, re.DOTALL)
    content = match.group(1)

    # remove content after h2 with span id='ดูเพิ่ม'
    pattern = r'<h2.*?>.*?<span.*?id="ดูเพิ่ม".*?>.*?</span>.*?</h2>'
    match = re.search(pattern, html)
    tag = match.group(0)
    index = re.search(re.escape(tag), content).start()
    content = content[:index]

    # find all a and li tag
    patterns = [r'<a.*?>(.*?)</a>', r'<li>(วัด.*?)</li>']
    temples = []

    for pattern in patterns:
        matches = re.findall(pattern, content)
        matches = filter_strings(matches, r'^วัด.*')
        temples.extend(matches)

    # split and get first index
    return [temple.split(' ')[0] for temple in temples]


@app.get("/")
def read_root():
    base_url = 'https://th.wikipedia.org/wiki/รายชื่อวัดในจังหวัด'
    urls = ['ราชบุรี', 'ลพบุรี', 'ลำปาง', 'ลำพูน']

    res = []
    for url in urls:
        res.append({url: fetch_data(base_url + url)})

    return res


# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host="localhost", port=8000)
