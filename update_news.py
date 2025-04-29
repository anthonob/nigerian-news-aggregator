# update_news.py

import os
import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import feedparser
from transformers import pipeline

# ─── PATH SETUP ────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
CSV_PATH    = os.path.join(BASE_DIR, "summarized_news.csv")
LOG_PATH    = os.path.join(BASE_DIR, "update_log.txt")

# ─── SUMMARIZER (light model) ──────────────────────────────────────────────────
summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6"
)

# ─── NEWS SOURCES ───────────────────────────────────────────────────────────────
RSS_FEEDS = {
    "Guardian Nigeria": "https://guardian.ng/feed/",
    "Vanguard Nigeria": "https://www.vanguardngr.com/feed/"
}
PUNCH_URL = "https://punchng.com/"

# ─── HELPERS ─────────────────────────────────────────────────────────────────────
def fetch_rss_articles(name, url):
    """Fetch top 5 items from a standard RSS feed."""
    feed = feedparser.parse(url)
    out = []
    for entry in feed.entries[:5]:
        text = BeautifulSoup(entry.summary, "html.parser").get_text()
        out.append({
            "Source": name,
            "Title": entry.title,
            "Link": entry.link,
            "Content": text
        })
    return out

def fetch_punch_articles():
    """Scrape the Punch homepage for latest <article> tags, fetch full text."""
    resp = requests.get(PUNCH_URL)
    soup = BeautifulSoup(resp.content, "html.parser")
    out = []
    for art in soup.find_all("article")[:5]:
        h3 = art.find("h3")
        if not h3: 
            continue
        a = h3.find("a")
        if not a or not a.get("href"):
            continue
        link = a["href"]
        title = a.get_text().strip()
        # Fetch full article text
        try:
            page = requests.get(link)
            psoup = BeautifulSoup(page.content, "html.parser")
            paras = psoup.find_all("p")
            content = " ".join([p.get_text() for p in paras])
        except:
            content = ""
        out.append({
            "Source": "Punch Nigeria",
            "Title": title,
            "Link": link,
            "Content": content
        })
    return out

def summarize_text(text: str) -> str:
    """Return a 30–70 word summary of text, or original if too short."""
    if not text or len(text.split()) < 50:
        return text.strip()
    # Huggingface summarizer wants tokens; limit to first 800 words
    snippet = " ".join(text.split()[:800])
    summary = summarizer(
        snippet,
        max_length=70,
        min_length=30,
        do_sample=False
    )[0]["summary_text"]
    return summary.strip()

# ─── MAIN UPDATE ────────────────────────────────────────────────────────────────
def update_news():
    try:
        articles = []
        # Guardian & Vanguard via RSS
        for name, url in RSS_FEEDS.items():
            articles += fetch_rss_articles(name, url)
        # Punch via scraping
        articles += fetch_punch_articles()

        df = pd.DataFrame(articles)
        df["Summary"] = df["Content"].apply(summarize_text)

        # Keep only relevant columns
        df = df[["Source", "Title", "Summary", "Link"]]

        # Save CSV
        df.to_csv(CSV_PATH, index=False)

        # Log success
        with open(LOG_PATH, "a", encoding="utf-8") as log:
            log.write(f"✅ Updated at {datetime.datetime.now()}\n")

    except Exception as e:
        with open(LOG_PATH, "a", encoding="utf-8") as log:
            log.write(f"❌ Error at {datetime.datetime.now()}: {e}\n")
        raise

if __name__ == "__main__":
    update_news()
