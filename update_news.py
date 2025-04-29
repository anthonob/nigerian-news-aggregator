# ─── INSTALL REQUIRED PACKAGES IF NEEDED ───────────────────────────────────────
# !pip install pandas requests feedparser beautifulsoup4 transformers

# ─── IMPORTS ───────────────────────────────────────────────────────────────────
import pandas as pd
import requests
from bs4 import BeautifulSoup
import feedparser
from transformers import pipeline
import os
import datetime

# ─── SETUP SUMMARIZER ──────────────────────────────────────────────────────────
summarizer = pipeline('summarization', model='facebook/bart-large-cnn')

# ─── PATH SETTINGS ─────────────────────────────────────────────────────────────
# Define where to save your CSV and Log files
BASE_FOLDER = r"C:\Users\USER\Documents\Personlaised News Aggregator"
SUMMARY_CSV_PATH = os.path.join(BASE_FOLDER, "summarized_news.csv")
LOG_FILE_PATH = os.path.join(BASE_FOLDER, "update_log.txt")

# ─── FUNCTIONS TO FETCH NEWS ────────────────────────────────────────────────────

def fetch_punch_news():
    url = 'https://punchng.com/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    articles = []
    for article in soup.find_all('article'):
        h3_tag = article.find('h3')
        if h3_tag:
            a_tag = h3_tag.find('a')
            if a_tag and a_tag.get('href'):
                title = a_tag.text.strip()
                link = a_tag['href']
                article_text = fetch_full_article_text(link)
                
                articles.append({
                    'Source': 'Punch Nigeria',
                    'Title': title,
                    'Link': link,
                    'Content': article_text
                })
    return articles

def fetch_full_article_text(link):
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        full_text = ' '.join([p.get_text() for p in paragraphs])
        return full_text.strip()
    except:
        return ""

def fetch_guardian_news():
    rss_url = "https://guardian.ng/feed/"
    feed = feedparser.parse(rss_url)
    
    articles = []
    for entry in feed.entries:
        summary = BeautifulSoup(entry.summary, 'html.parser').text
        articles.append({
            'Source': 'Guardian Nigeria',
            'Title': entry.title,
            'Link': entry.link,
            'Content': summary
        })
    return articles

def fetch_vanguard_news():
    rss_url = "https://www.vanguardngr.com/feed/"
    feed = feedparser.parse(rss_url)
    
    articles = []
    for entry in feed.entries:
        summary = BeautifulSoup(entry.summary, 'html.parser').text
        articles.append({
            'Source': 'Vanguard Nigeria',
            'Title': entry.title,
            'Link': entry.link,
            'Content': summary
        })
    return articles

def generate_summary(text):
    if not text or len(text.split()) < 50:
        return text
    try:
        words = text.split()[:500]
        short_text = ' '.join(words)
        summary_text = summarizer(
            short_text,
            max_length=100,
            min_length=30,
            do_sample=False
        )[0]['summary_text']
        return summary_text
    except Exception as e:
        print(f"Summarization error: {e}")
        return text

# ─── MAIN UPDATE FUNCTION ──────────────────────────────────────────────────────

def update_news():
    try:
        print("Fetching news...")
        punch_articles = fetch_punch_news()
        guardian_articles = fetch_guardian_news()
        vanguard_articles = fetch_vanguard_news()

        all_articles = punch_articles + guardian_articles + vanguard_articles
        news_df = pd.DataFrame(all_articles)

        # Drop duplicates and limit to top 20
        news_df = news_df.drop_duplicates(subset='Title').reset_index(drop=True)
        news_df = news_df.head(20)

        print("Summarizing news...")
        news_df['Summary'] = news_df['Content'].apply(generate_summary)

        print("Saving summarized news to file...")

        # Delete old CSV if it exists
        if os.path.exists(SUMMARY_CSV_PATH):
            os.remove(SUMMARY_CSV_PATH)

        # Save new CSV
        news_df.to_csv(SUMMARY_CSV_PATH, index=False)

        # Log success (UTF-8 encoding to handle emojis ✅)
        with open(LOG_FILE_PATH, 'a', encoding='utf-8') as log:
            log.write(f"✅ News updated successfully at {datetime.datetime.now()}\n")

        print("Update completed successfully.")

    except Exception as e:
        # Log error
        with open(LOG_FILE_PATH, 'a', encoding='utf-8') as log:
            log.write(f"❌ Error at {datetime.datetime.now()}: {str(e)}\n")
        print(f"Error occurred: {str(e)}")

# ─── EXECUTE SCRIPT ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    update_news()
