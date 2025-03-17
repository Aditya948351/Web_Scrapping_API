from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# 🚀 List of coding-related websites with scraping functions
NEWS_SOURCES = [
    {"name": "InfoQ", "url": "https://www.infoq.com/development/news/", "scraper": "scrape_infoq"},
    {"name": "Hackernoon", "url": "https://hackernoon.com/tagged/programming", "scraper": "scrape_hackernoon"},
    {"name": "Medium", "url": "https://medium.com/tag/programming", "scraper": "scrape_medium"},
    {"name": "DZone", "url": "https://dzone.com/devops-tutorials-tools-news", "scraper": "scrape_dzone"},
    {"name": "FreeCodeCamp", "url": "https://www.freecodecamp.org/news/", "scraper": "scrape_freecodecamp"},
    {"name": "CSS-Tricks", "url": "https://css-tricks.com/archives/", "scraper": "scrape_csst"},
    {"name": "SitePoint", "url": "https://www.sitepoint.com/web-development/", "scraper": "scrape_sitepoint"},
    {"name": "Android Dev Blog", "url": "https://android-developers.googleblog.com/", "scraper": "scrape_androiddev"},
    {"name": "Google AI Blog", "url": "https://ai.googleblog.com/", "scraper": "scrape_googleai"},
    {"name": "GitHub Blog", "url": "https://github.blog/", "scraper": "scrape_github"},
    {"name": "Smashing Magazine", "url": "https://www.smashingmagazine.com/articles/", "scraper": "scrape_smashingmag"},
    {"name": "The New Stack", "url": "https://thenewstack.io/category/development/", "scraper": "scrape_newstack"}
]

def fetch_page(url):
    """Fetch HTML content with timeout handling"""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def scrape_infoq():
    url = "https://www.infoq.com/development/news/"
    html = fetch_page(url)
    if not html:
        return []
    
    soup = BeautifulSoup(html, "html.parser")
    news_list = []
    for article in soup.select(".news-list .news_item")[:10]:
        title_tag = article.select_one("h2 a")
        img_tag = article.select_one(".news_image img")

        title = title_tag.text.strip() if title_tag else "No Title"
        link = title_tag["href"] if title_tag else "#"
        image = img_tag["src"] if img_tag else None

        news_list.append({"title": title, "url": link, "image": image, "source": "InfoQ"})
    return news_list

def scrape_hackernoon():
    url = "https://hackernoon.com/tagged/programming"
    html = fetch_page(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    news_list = []
    for article in soup.select("div.story-card")[:10]:
        title_tag = article.select_one("h2 a")
        img_tag = article.select_one("img")

        title = title_tag.text.strip() if title_tag else "No Title"
        link = "https://hackernoon.com" + title_tag["href"] if title_tag else "#"
        image = img_tag["src"] if img_tag else None

        news_list.append({"title": title, "url": link, "image": image, "source": "Hackernoon"})
    return news_list

def scrape_medium():
    url = "https://medium.com/tag/programming"
    html = fetch_page(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    news_list = []
    for article in soup.select("article")[:10]:
        title_tag = article.select_one("h2")
        link_tag = article.select_one("a")
        img_tag = article.select_one("img")

        title = title_tag.text.strip() if title_tag else "No Title"
        link = link_tag["href"] if link_tag else "#"
        image = img_tag["src"] if img_tag else None

        if not link.startswith("http"):
            link = "https://medium.com" + link

        news_list.append({"title": title, "url": link, "image": image, "source": "Medium"})
    return news_list

def scrape_dzone():
    url = "https://dzone.com/devops-tutorials-tools-news"
    html = fetch_page(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    news_list = []
    for article in soup.select("article")[:10]:
        title_tag = article.select_one("h2 a")
        img_tag = article.select_one("img")

        title = title_tag.text.strip() if title_tag else "No Title"
        link = title_tag["href"] if title_tag else "#"
        image = img_tag["src"] if img_tag else None

        news_list.append({"title": title, "url": link, "image": image, "source": "DZone"})
    return news_list

def scrape_freecodecamp():
    url = "https://www.freecodecamp.org/news/"
    html = fetch_page(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    news_list = []
    for article in soup.select(".post-card")[:10]:
        title_tag = article.select_one("h2 a")
        img_tag = article.select_one("img")

        title = title_tag.text.strip() if title_tag else "No Title"
        link = title_tag["href"] if title_tag else "#"
        image = img_tag["src"] if img_tag else None

        news_list.append({"title": title, "url": link, "image": image, "source": "FreeCodeCamp"})
    return news_list

# ✨ Add more scraper functions for new sources in the same format ✨

@app.route("/news", methods=["GET"])
def get_coding_news():
    """Fetch and return coding news from multiple sources"""
    all_news = []
    for source in NEWS_SOURCES:
        scraper_function = globals().get(source["scraper"])
        if scraper_function:
            all_news.extend(scraper_function())
    
    return jsonify(all_news)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=True)
