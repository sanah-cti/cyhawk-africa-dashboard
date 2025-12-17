import streamlit as st
import pandas as pd
import os
import re
import urllib.parse
from datetime import datetime

# ----------------------------------------
# Page Config & Branding
# ----------------------------------------
try:
    from navigation_utils import add_logo_and_branding, set_page_config as custom_set_page_config
    custom_set_page_config(
        page_title="Threat Actors | CyHawk Africa",
        page_icon="🎯",
        layout="wide"
    )
    add_logo_and_branding()
except ImportError:
    st.set_page_config(
        page_title="Threat Actors | CyHawk Africa",
        page_icon="🎯",
        layout="wide"
    )

# ----------------------------------------
# Theme
# ----------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

CYHAWK_RED = "#C41E3A"
CYHAWK_RED_DARK = "#9A1529"

# ----------------------------------------
# Utilities
# ----------------------------------------
def slugify(name: str) -> str:
    """
    Convert actor name to SEO-friendly slug
    """
    name = name.lower().strip()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[\s_-]+", "-", name)
    return name

# ----------------------------------------
# Load Data
# ----------------------------------------
@st.cache_data
def load_data():
    path = "data/incidents.csv"
    if not os.path.exists(path):
        return pd.DataFrame()

    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    for col in ["actor", "country", "sector", "severity"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str)

    return df

df = load_data()

# ----------------------------------------
# Threat Actor Profiles (Metadata)
# ----------------------------------------
ACTOR_PROFILES = {
    "Keymous Plus": {
        "alias": "Unknown",
        "origin": "Unknown",
        "active_since": "Unknown",
        "type": "Unclassified"
    },
    "APT28": {
        "alias": "Fancy Bear, Sofacy",
        "origin": "Russia",
        "active_since": "2007",
        "type": "State-Sponsored (GRU)"
    },
    "Lazarus Group": {
        "alias": "HIDDEN COBRA",
        "origin": "North Korea",
        "active_since": "2009",
        "type": "State-Sponsored (RGB)"
    }
}

# ----------------------------------------
# Header
# ----------------------------------------
st.markdown(f"""
<div style="
    background: linear-gradient(135deg, {CYHAWK_RED} 0%, {CYHAWK_RED_DARK} 100%);
    padding: 3rem;
    border-radius: 14px;
    text-align: center;
    margin-bottom: 2rem;
">
    <h1 style="color:white; margin:0;">Threat Actor Intelligence</h1>
    <p style="color:rgba(255,255,255,0.9); margin-top:0.5rem;">
        Comprehensive profiles of active threat actors targeting African organizations
    </p>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------
# Actor Statistics
# ----------------------------------------
if df.empty:
    st.warning("No threat actor data available.")
    st.stop()

actor_stats = (
    df.groupby("actor")
    .agg(
        total_attacks=("date", "count"),
        high_severity=("severity", lambda x: (x == "High").sum()),
        countries=("country", "nunique"),
        sectors=("sector", "nunique")
    )
    .reset_index()
)

actor_stats["slug"] = actor_stats["actor"].apply(slugify)

# ----------------------------------------
# Filters
# ----------------------------------------
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    search = st.text_input("Search Threat Actors", placeholder="Search by name...")

with col2:
    sort_by = st.selectbox("Sort By", ["Total Attacks", "Alphabetical"])

with col3:
    limit = st.selectbox("Show", [12, 24, "All"])

# ----------------------------------------
# Apply Filters
# ----------------------------------------
filtered = actor_stats.copy()

if search:
    filtered = filtered[filtered["actor"].str.contains(search, case=False)]

if sort_by == "Alphabetical":
    filtered = filtered.sort_values("actor")
else:
    filtered = filtered.sort_values("total_attacks", ascending=False)

if limit != "All":
    filtered = filtered.head(int(limit))

# ----------------------------------------
# Display Cards
# ----------------------------------------
cols = 4
rows = range(0, len(filtered), cols)

for i in rows:
    cards = st.columns(cols)
    for idx, col in enumerate(cards):
        if i + idx >= len(filtered):
            continue

        row = filtered.iloc[i + idx]
        profile = ACTOR_PROFILES.get(row["actor"], {})

        profile_url = f"/Actor_Profile?actor_slug={urllib.parse.quote(row['slug'])}"

        with col:
            st.markdown(f"""
            <div style="
                border:1px solid #30363d;
                border-radius:12px;
                padding:1.25rem;
                height:100%;
                background:#0d1117;
            ">
                <h3 style="margin-top:0;">{row['actor']}</h3>
                <p style="color:#8b949e; font-size:0.85rem;">
                    {profile.get("alias", "Unknown")}
                </p>

                <div style="font-size:0.85rem; margin-bottom:1rem;">
                    <div><strong>Origin:</strong> {profile.get("origin", "Unknown")}</div>
                    <div><strong>Type:</strong> {profile.get("type", "Unknown")}</div>
                </div>

                <div style="display:flex; gap:1rem; font-size:0.85rem;">
                    <div><strong>{row['total_attacks']}</strong><br>Attacks</div>
                    <div><strong>{row['countries']}</strong><br>Countries</div>
                    <div><strong>{row['sectors']}</strong><br>Sectors</div>
                </div>

                <a href="{profile_url}" target="_blank"
                   style="
                        display:block;
                        margin-top:1rem;
                        text-align:center;
                        padding:0.6rem;
                        background:{CYHAWK_RED};
                        color:white;
                        border-radius:6px;
                        text-decoration:none;
                        font-weight:600;
                   ">
                    View Profile
                </a>
            </div>
            """, unsafe_allow_html=True)

# ----------------------------------------
# Footer Info
# ----------------------------------------
st.markdown("---")
st.info(f"Showing {len(filtered)} threat actors")
