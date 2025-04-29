# news_app.py

import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Eagle Nigerian News",
    page_icon="🦅",
    layout="wide",
)

# ─── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown(
    """
    # 🦅 Eagle Nigerian News
    #### Your Smart AI-Powered Daily News Digest 🇳🇬
    ---
    """,
    unsafe_allow_html=True,
)

# ─── LAST UPDATED ───────────────────────────────────────────────────────────────
csv_path = os.path.join(os.path.dirname(__file__), "summarized_news.csv")
if os.path.exists(csv_path):
    lm = datetime.fromtimestamp(os.path.getmtime(csv_path))
    st.write(f"🕒 **Last Updated:** {lm.strftime('%d %B %Y, %I:%M %p')}")

# ─── LOAD & DISPLAY ─────────────────────────────────────────────────────────────
news_df = pd.read_csv(csv_path)

st.write(f"### 📰 Latest Headlines ({len(news_df)} stories)")

for _, row in news_df.iterrows():
    st.subheader(row["Title"])
    st.caption(f"**Source:** {row['Source']}")
    st.write(row["Summary"])
    st.markdown(f"[🔗 Read Full Article Here]({row['Link']})")
    st.markdown("---")
