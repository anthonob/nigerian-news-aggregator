# update_news.py

import os
import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import feedparser
from transformers import pipeline

# ─── PATH SETUP ────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
CSV_PATH  = os.path.join(BASE_DIR, "summarized_news.csv")
LOG_PATH  = os.path.join(BASE_DIR, "update_log.txt")

# ─── SUMMARIZER ────────────────────────────────────────────────────────────────
summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6",
    tokenizer="sshleifer/distilbart-cnn-12-6"
)

# ─── NEWS SOURCES ───────────────────────────────────────────────────────────────
RSS_FEEDS = {
    "Guardian Nigeria": "https://guardian.ng/feed/",
    "Vanguard Nigeria": "https://www.vanguardngr.com/feed/"
}
PUNCH_URL = "https://punchng.com/"

# ─── HELPERS ─────────────────────────────────────────────────────────────────────
def fetch_rss_articles(name, url):
    feed = feedparser.parse(url)
    out = []
    for entry in feed.entries[:5]:
        summary = BeautifulSoup(entry.summary, "html.parser").get_text()
        out.append({
            "Source":  name,
            "Title":   entry.title,
            "Link":    entry.link,
            "Content": summary
        })
    return out

def fetch_punch_articles():
    resp = requests.get(PUNCH_URL)
    soup = BeautifulSoup(resp.content, "html.parser")
    out = []
    for art in soup.find_all("article")[:5]:
        h3 = art.find("h3")
        if not h3 or not (a := h3.find("a")) or not a.get("href"):
            continue
        link  = a["href"]
        title = a.get_text().strip()
        # fetch full text
        try:
            page = requests.get(link)
            psoup = BeautifulSoup(page.content, "html.parser")
            paras = psoup.find_all("p")
            content = " ".join(p.get_text() for p in paras)
        except:
            content = ""
        out.append({
            "Source":  "Punch Nigeria",
            "Title":   title,
            "Link":    link,
            "Content": content
        })
    return out

def summarize_text(text: str) -> str:
    if not text or len(text.split()) < 30:
        return text.strip()
    # Truncate input to first ~1024 tokens via truncation=True
    result = summarizer(
        text,
        max_length=70,
        min_length=30,
        do_sample=False,
        truncation=True
    )[0]["summary_text"]
    return result.strip()

# ─── MAIN UPDATE ────────────────────────────────────────────────────────────────
def update_news():
    try:
        articles = []
        # RSS sources
        for name, url in RSS_FEEDS.items():
            articles += fetch_rss_articles(name, url)
        # Punch via scraping
        articles += fetch_punch_articles()

        df = pd.DataFrame(articles)
        df["Summary"] = df["Content"].apply(summarize_text)
        df = df[["Source","Title","Summary","Link"]]

        df.to_csv(CSV_PATH, index=False)

        with open(LOG_PATH, "a", encoding="utf-8") as log:
            log.write(f"✅ Updated at {datetime.datetime.now()}\n")

    except Exception as e:
        with open(LOG_PATH, "a", encoding="utf-8") as log:
            log.write(f"❌ Error at {datetime.datetime.now()}: {e}\n")
        raise

if __name__ == "__main__":
    update_news()
