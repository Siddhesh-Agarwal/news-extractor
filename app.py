from typing import List, Tuple
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request


def is_valid_source(source: str) -> bool:
    image_extensions = ["jpg", "png", "jpeg"]
    return any(source.endswith(ext) for ext in image_extensions)

def get_news(url: str) -> Tuple[List[str], str]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.114 Safari/537.36"
    }
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")

        # Get image source
        images = soup.find_all("source")
        source = ""
        for img in images:
            if is_valid_source(img["srcset"]):
                source = img["srcset"]
                break
        if not is_valid_source(source):
            images = soup.find_all("img")
            for img in images:
                if is_valid_source(img["src"]):
                    source = img["src"]
                    break
        # print(f"{source=}")

        # fetch news and clean it
        news = soup.find_all("p")
        clean_news = []
        for item in news:
            item = item.text.strip()
            if len(item) > 50:
                clean_news.append(item)

        return clean_news, source
    return [], ""


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", news=[])


@app.route("/", methods=["POST"])
def news():
    url = request.form["url"]
    news, src = get_news(url)
    src = src.strip()
    if src == "":
        return render_template("index.html", news=news, url=url)
    return render_template("index.html", news=news, url=url, src=src)


if __name__ == "__main__":
    app.run(debug=True)
