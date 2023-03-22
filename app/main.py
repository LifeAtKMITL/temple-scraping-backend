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
    response = requests.get(url)

    scraped_text = response.text

    # match div with class mw-parser-output to the line with the word "ดูเพิ่ม"
    regex = r'^.*?<div class="mw-parser-output">((?:.*\n)*?)^.*?ดูเพิ่ม.*$'

    match = re.search(regex, scraped_text, re.MULTILINE)

    if match:
        container_content = match.group(1)

        li_pattern = r'<li>.*?(วัด[ก-์0-9]*).*?</li>'
        result = re.findall(li_pattern, container_content, re.MULTILINE)

        return result
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
