# update_news.py

import os
import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import feedparser
from transformers import pipeline

# ─── PATHS ─────────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
SUMMARY_CSV   = os.path.join(BASE_DIR, "summarized_news.csv")
LOG_FILE      = os.path.join(BASE_DIR, "update_log.txt")

# ─── SUMMARIZER ────────────────────────────────────────────────────────────────
summarizer = pipeline(
    'summarization',
    model='sshleifer/distilbart-cnn-12-6'
)

# ─── NEWS SOURCES ───────────────────────────────────────────────────────────────
RSS_FEEDS = {
    "Guardian Nigeria": "https://guardian.ng/feed/",
    "Punch Nigeria":    "https://punchng.com/feed/",
    "Vanguard Nigeria": "https://www.vanguardngr.com/feed/"
}

# ─── HELPERS ─────────────────────────────────────────────────────────────────────
def fetch_rss(feed_url):
    feed = feedparser.parse(feed_url)
    articles = []
    for entry in feed.entries[:5]:
        summary = BeautifulSoup(entry.summary, 'html.parser').get_text()
        articles.append({
            "Title":   entry.title,
            "Link":    entry.link,
            "Content": summary
        })
    return articles

def fetch_full_article_text(url):
    try:
        resp = requests.get(url)
        soup = BeautifulSoup(resp.content, "html.parser")
        paras = soup.find_all("p")
        return " ".join([p.get_text() for p in paras])
    except:
        return ""

def summarize(text):
    if not text or len(text.split()) < 30:
        return text
    return summarizer(text, max_length=100, min_length=30, do_sample=False)[0]['summary_text']

# ─── MAIN ───────────────────────────────────────────────────────────────────────
def update_news():
    try:
        all_news = []
        for source, url in RSS_FEEDS.items():
            items = fetch_rss(url)
            for art in items:
                content = art["Content"]
                # for Punch, if RSS summary too short, fetch full article
                if source == "Punch Nigeria" and len(content.split()) < 50:
                    content = fetch_full_article_text(art["Link"])
                all_news.append({
                    "Source":  source,
                    "Title":   art["Title"],
                    "Link":    art["Link"],
                    "Content": content
                })

        df = pd.DataFrame(all_news)
        df["Summary"] = df["Content"].apply(summarize)
        df[["Source","Title","Summary","Link"]].to_csv(SUMMARY_CSV, index=False)

        with open(LOG_FILE, "a", encoding="utf-8") as log:
            log.write(f"✅ Updated at {datetime.datetime.now()}\n")

    except Exception as e:
        with open(LOG_FILE, "a", encoding="utf-8") as log:
            log.write(f"❌ Error at {datetime.datetime.now()}: {e}\n")

if __name__ == "__main__":
    update_news()
