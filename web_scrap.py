import json
import os
import random
from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

NEWS_SOURCES = {
    "Hacker News": {"url": "https://news.ycombinator.com/", "selectors": {"article": ".athing", "title": ".storylink", "link": ".storylink"}},
    "FreeCodeCamp": {"url": "https://www.freecodecamp.org/news/", "selectors": {"article": ".post-card", "title": "h2 a", "link": "h2 a", "image": "img"}},
    "Ars Technica": {"url": "https://arstechnica.com/information-technology/", "selectors": {"article": "li.article", "title": "h2 a", "link": "h2 a", "image": "img"}},
    "InfoQ": {"url": "https://www.infoq.com/development/news/", "selectors": {"article": ".news-list .news_item", "title": "h2 a", "link": "h2 a", "image": ".news_image img"}},
    "TechCrunch": {"url": "https://techcrunch.com/startups/", "selectors": {"article": "article", "title": "h2 a", "link": "h2 a", "image": "img"}},
    "Dev.to": {"url": "https://dev.to/", "selectors": {"article": ".crayons-story", "title": "h2 a", "link": "h2 a", "image": "img"}},
    "Google AI Blog": {"url": "https://ai.googleblog.com/", "selectors": {"article": ".date-outer", "title": ".post-title.entry-title a", "link": ".post-title.entry-title a"}},
    "NVIDIA Developer Blog": {"url": "https://developer.nvidia.com/blog/", "selectors": {"article": "article", "title": "h2 a", "link": "h2 a", "image": "img"}},
    "JetBrains Blog": {"url": "https://blog.jetbrains.com/", "selectors": {"article": ".post-item", "title": ".post-title a", "link": ".post-title a", "image": "img"}},
    "Stack Overflow Blog": {"url": "https://stackoverflow.blog/", "selectors": {"article": ".post", "title": "h2 a", "link": "h2 a", "image": "img"}},
    "OpenAI Blog": {"url": "https://openai.com/research/", "selectors": {"article": ".post", "title": "h3 a", "link": "h3 a", "image": "img"}},
    "Smashing Magazine": {"url": "https://www.smashingmagazine.com/articles/", "selectors": {"article": "article", "title": "h2 a", "link": "h2 a", "image": "img"}},
    "TechCrunch": {"url": "https://techcrunch.com/startups/", "selectors": {"article": "article", "title": "h2 a", "link": "h2 a", "image": "img"}},
    "Dev.to": {"url": "https://dev.to/", "selectors": {"article": ".crayons-story", "title": "h2 a", "link": "h2 a", "image": "img"}},
    "Google AI Blog": {"url": "https://ai.googleblog.com/", "selectors": {"article": ".date-outer", "title": ".post-title.entry-title a", "link": ".post-title.entry-title a"}},
    "NVIDIA Developer Blog": {"url": "https://developer.nvidia.com/blog/", "selectors": {"article": "article", "title": "h2 a", "link": "h2 a", "image": "img"}},
    "JetBrains Blog": {"url": "https://blog.jetbrains.com/", "selectors": {"article": ".post-item", "title": ".post-title a", "link": ".post-title a", "image": "img"}},
    "Stack Overflow Blog": {"url": "https://stackoverflow.blog/", "selectors": {"article": ".post", "title": "h2 a", "link": "h2 a", "image": "img"}},
    "OpenAI Blog": {"url": "https://openai.com/research/", "selectors": {"article": ".post", "title": "h3 a", "link": "h3 a", "image": "img"}},
    "MIT Technology Review": {"url": "https://www.technologyreview.com/topic/artificial-intelligence/", "selectors": {"article": ".river__item", "title": "h3 a", "link": "h3 a", "image": "img"}},
    "Android Developers Blog": {"url": "https://android-developers.googleblog.com/", "selectors": {"article": ".post-outer", "title": "h3 a", "link": "h3 a", "image": "img"}},
    "GitHub Trending": {"url": "https://github.com/trending", "selectors": {}}
}

def fetch_page(url):
    """Fetch HTML page content safely."""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return None

def scrape_news(source_name, config):
    """Scrapes news articles from a given source."""
    if source_name == "GitHub Trending":
        return get_github_trending()

    html = fetch_page(config["url"])
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    news_list = []

    for article in soup.select(config["selectors"]["article"])[:5]:  # Get top 5 articles
        title_tag = article.select_one(config["selectors"]["title"])
        link_tag = article.select_one(config["selectors"]["link"])
        img_tag = article.select_one(config["selectors"].get("image", ""))

        title = title_tag.text.strip() if title_tag else "No Title"
        link = link_tag["href"] if link_tag else "#"
        image = img_tag["src"] if img_tag and "src" in img_tag.attrs else None

        if "base_url" in config and not link.startswith("http"):
            link = config["base_url"] + link

        news_list.append({"source": source_name, "title": title, "url": link, "image": image})

    return news_list

def get_github_trending():
    """Scrapes GitHub trending repositories."""
    url = "https://github.com/trending"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    articles = []

    for repo in soup.find_all("article", class_="Box-row")[:5]:  # Get top 5 trending
        title = repo.find("h2").text.strip().replace("\n", "").replace(" ", "")
        repo_url = "https://github.com" + repo.find("h2").find("a")["href"]
        image = "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"

        articles.append({"source": "GitHub Trending", "title": title, "url": repo_url, "image": image})

    return articles

@app.route('/news', methods=['GET'])
def get_coding_news():
    """Fetches news from random sources and shuffles output."""
    try:
        selected_sources = random.sample(list(NEWS_SOURCES.keys()), 8)  # Select 8 random sources
        all_news = []

        for source in selected_sources:
            all_news.extend(scrape_news(source, NEWS_SOURCES[source]))

        random.shuffle(all_news)  # Shuffle news articles to avoid repetition

        return jsonify(all_news[:15])  # Limit response to 15 articles
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=True)
