import os
import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
import feedparser

# ─── PATHS ─────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUMMARY_CSV_PATH = os.path.join(BASE_DIR, "summarized_news.csv")
LOG_FILE_PATH = os.path.join(BASE_DIR, "update_log.txt")

# ─── NEWS SOURCES ───────────────────────────────────────────────────────────────
RSS_FEEDS = {
    "Guardian Nigeria": "https://guardian.ng/feed/",
    "Punch Nigeria": "https://punchng.com/feed/",
    "Vanguard Nigeria": "https://www.vanguardngr.com/feed/"
}

# ─── SUMMARIZER ─────────────────────────────────────────────────────────────────
summarizer = pipeline('summarization', model='facebook/bart-large-cnn')

# ─── HELPER FUNCTIONS ───────────────────────────────────────────────────────────
def fetch_rss_articles(feed_url):
    feed = feedparser.parse(feed_url)
    articles = []
    for entry in feed.entries[:5]:  # Limit to latest 5 articles per source
        articles.append({
            "Title": entry.title,
            "Link": entry.link,
            "Content": entry.summary if hasattr(entry, 'summary') else ""
        })
    return articles

def fetch_website_articles(url, article_tag='article', title_tag='h3'):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = []
    for article in soup.find_all(article_tag):
        h3_tag = article.find(title_tag)
        if h3_tag:
            a_tag = h3_tag.find('a')
            if a_tag and a_tag.get('href'):
                articles.append({
                    "Title": a_tag.text.strip(),
                    "Link": a_tag['href'],
                    "Content": ""
                })
    return articles

def summarize_text(text):
    if not text or len(text.split()) < 30:
        return text
    summary = summarizer(text, max_length=100, min_length=30, do_sample=False)[0]['summary_text']
    return summary

# ─── MAIN UPDATE FUNCTION ───────────────────────────────────────────────────────
def update_news():
    try:
        print("Fetching news...")
        news_data = []

        for source, feed_url in RSS_FEEDS.items():
            if "punchng.com" in feed_url:
                articles = fetch_website_articles('https://punchng.com/')
            else:
                articles = fetch_rss_articles(feed_url)

            for article in articles:
                news_data.append({
                    "Source": source,
                    "Title": article["Title"],
                    "Link": article["Link"],
                    "Content": article["Content"]
                })

        print("Summarizing news...")
        news_df = pd.DataFrame(news_data)
        news_df['Summary'] = news_df['Content'].apply(summarize_text)

        print("Saving summarized news to file...")
        news_df[['Source', 'Title', 'Summary', 'Link']].to_csv(SUMMARY_CSV_PATH, index=False)

        # Save success log
        with open(LOG_FILE_PATH, 'a', encoding='utf-8') as log:
            log.write(f"✅ Updated successfully at {datetime.datetime.now()}\n")

    except Exception as e:
        print(f"Error: {str(e)}")
        with open(LOG_FILE_PATH, 'a', encoding='utf-8') as log:
            log.write(f"❌ Error at {datetime.datetime.now()}: {str(e)}\n")

# ─── RUN ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    update_news()
