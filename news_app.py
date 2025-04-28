# ─── INSTALL REQUIRED PACKAGES IF NEEDED ───────────────────────────────────────
# !pip install streamlit pandas

# ─── IMPORTS ───────────────────────────────────────────────────────────────────
import streamlit as st
import pandas as pd

# ─── STREAMLIT APP ─────────────────────────────────────────────────────────────

# Page configuration
st.set_page_config(page_title="Nigeria News Aggregator", page_icon="📰", layout="wide")

st.title("📰 Live Nigeria News Aggregator")
st.markdown("Get high-quality, summarized headlines from Punch, Guardian, and Vanguard Newspapers.")

# Load summarized news from CSV
news_df = pd.read_csv('summarized_news.csv')

# Optional: Show last updated time based on file save time
import os
import datetime

last_modified_timestamp = os.path.getmtime('summarized_news.csv')
last_updated_time = datetime.datetime.fromtimestamp(last_modified_timestamp)
st.markdown(f"**Last Updated:** {last_updated_time.strftime('%B %d, %Y %I:%M %p')}")

# Sidebar filters
st.sidebar.header("Filter News")
selected_source = st.sidebar.multiselect(
    "Select News Source(s):",
    options=news_df['Source'].unique(),
    default=news_df['Source'].unique()
)

# Filter based on sidebar selection
filtered_df = news_df[news_df['Source'].isin(selected_source)]

# Show news
for idx, row in filtered_df.iterrows():
    st.subheader(row['Title'])
    st.markdown(f"**Source:** {row['Source']}")
    st.write(row['Summary'])
    st.markdown(f"[Read Full Article Here]({row['Link']})")
    st.markdown("---")
