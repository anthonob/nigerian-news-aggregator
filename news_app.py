# ─── IMPORTS ───────────────────────────────────────────────────────────────────
import streamlit as st
import pandas as pd

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

# ─── LOAD SUMMARIZED NEWS ──────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('summarized_news.csv')
    return df

news_df = load_data()

# ─── DISPLAY NEWS ──────────────────────────────────────────────────────────────
st.write(f"### 📰 Latest Headlines ({len(news_df)} stories)")

for index, row in news_df.iterrows():
    st.subheader(f"{row['Title']}")
    st.caption(f"**Source:** {row['Source']}")
    st.write(f"{row['Summary']}")
    st.markdown(f"[Read Full Article Here]({row['Link']})")
    st.markdown("---")
