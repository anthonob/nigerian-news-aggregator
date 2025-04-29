# ─── IMPORTS ───────────────────────────────────────────────────────────────────
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ─── PAGE CONFIGURATION ────────────────────────────────────────────────────────
st.set_page_config(page_title="Eagle Nigerian News", page_icon="🦅", layout="wide")

# ─── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown(
    """
    # 🦅 Eagle Nigerian News
    #### Your Smart AI-Powered Daily News Digest 🇳🇬
    ---
    """,
    unsafe_allow_html=True
)

# ─── SHOW LAST UPDATED TIME ─────────────────────────────────────────────────────
csv_path = 'summarized_news.csv'
if os.path.exists(csv_path):
    last_modified = datetime.fromtimestamp(os.path.getmtime(csv_path))
    st.write(f"🕒 **Last Updated:** {last_modified.strftime('%d %B %Y, %I:%M %p')}")

# ─── LOAD SUMMARIZED NEWS ──────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv(csv_path)
    return df

news_df = load_data()

# ─── DISPLAY NEWS ──────────────────────────────────────────────────────────────
st.write(f"### 📰 Latest Headlines ({len(news_df)} stories)")

for index, row in news_df.iterrows():
    st.subheader(f"{row['Title']}")
    st.caption(f"**Source:** {row['Source']}")
    st.write(f"{row['Summary']}")
    st.markdown(f"[🔗 Read Full Article Here]({row['Link']})")
    st.markdown("---")

# news_app.py

import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Eagle Nigerian News", page_icon="🦅", layout="wide")

# ─── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown(
    """
    # 🦅 Eagle Nigerian News
    #### Your Smart AI-Powered Daily News Digest 🇳🇬
    ---
    """,
    unsafe_allow_html=True
)

# ─── LAST UPDATED TIMESTAMP ──────────────────────────────────────────────────────
csv_path = 'summarized_news.csv'
if os.path.exists(csv_path):
    last_mod = datetime.fromtimestamp(os.path.getmtime(csv_path))
    st.write(f"🕒 **Last Updated:** {last_mod.strftime('%d %B %Y, %I:%M %p')}")

# ─── LOAD DATA (no cache, always fresh) ──────────────────────────────────────────
news_df = pd.read_csv(csv_path)

# ─── DISPLAY NEWS ──────────────────────────────────────────────────────────────
st.write(f"### 📰 Latest Headlines ({len(news_df)} stories)")

for _, row in news_df.iterrows():
    st.subheader(row["Title"])
    st.caption(f"**Source:** {row['Source']}")
    st.write(row["Summary"])
    st.markdown(f"[🔗 Read Full Article Here]({row['Link']})")
    st.markdown("---")
