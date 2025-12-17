import streamlit as st
import pandas as pd
from datetime import datetime
import os

# -------------------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Threat Actor Intelligence | CyHawk Africa",
    page_icon="assets/favicon.ico",
    layout="wide"
)

# -------------------------------------------------------------------
# BRANDING
# -------------------------------------------------------------------
CYHAWK_RED = "#C41E3A"
CYHAWK_DARK = "#0D1117"
CARD_BG = "#161B22"
BORDER = "#30363D"
TEXT_MUTED = "#8B949E"

# -------------------------------------------------------------------
# HEADER (HERO)
# -------------------------------------------------------------------
st.markdown(
    """
    <style>
    .hero {
        background: linear-gradient(135deg, #C41E3A 0%, #9A1529 100%);
        padding: 3.5rem 2rem;
        border-radius: 14px;
        text-align: center;
        margin-bottom: 2.5rem;
    }
    .hero h1 {
        color: #ffffff;
        font-size: 2.6rem;
        font-weight: 800;
        margin-bottom: 0.6rem;
    }
    .hero p {
        color: rgba(255,255,255,0.9);
        font-size: 1.05rem;
        max-width: 720px;
        margin: 0 auto;
        line-height: 1.6;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="hero">
        <h1>Threat Actor Intelligence</h1>
        <p>
            Comprehensive profiles of active threat actors targeting African organizations
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------------------------
# LOAD DATA (SAFE FALLBACK)
# -------------------------------------------------------------------
@st.cache_data
def load_data():
    if os.path.exists("data/incidents.csv"):
        df = pd.read_csv("data/incidents.csv")
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
        return df
    return pd.DataFrame()

df = load_data()

# -------------------------------------------------------------------
# ACTOR METRICS
# -------------------------------------------------------------------
if not df.empty:
    stats = df.groupby("actor").agg(
        attacks=("date", "count"),
        countries=("country", "nunique"),
        sectors=("sector", "nunique")
    ).reset_index()
else:
    stats = pd.DataFrame(columns=["actor", "attacks", "countries", "sectors"])

# -------------------------------------------------------------------
# ACTOR PROFILES (STATIC ENRICHMENT)
# -------------------------------------------------------------------
ACTOR_META = {
    "Keymous Plus": {"origin": "Unknown", "type": "Unclassified", "active": "Since Unknown"},
    "OurSec": {"origin": "Unknown", "type": "Unclassified", "active": "Since Unknown"},
    "Funksec": {"origin": "Unknown", "type": "Unclassified", "active": "Since Unknown"},
    "dark hell 07x": {"origin": "Unknown", "type": "Unclassified", "active": "Since Unknown"},
    "FireWire": {"origin": "Unknown", "type": "Unclassified", "active": "Since Unknown"},
    "Devman": {"origin": "Unknown", "type": "Unclassified", "active": "Since Unknown"},
    "SKYZZXPLOIT": {"origin": "Unknown", "type": "Unclassified", "active": "Since Unknown"},
    "hider_nex": {"origin": "Unknown", "type": "Unclassified", "active": "Since Unknown"},
    "Nightspire": {"origin": "Unknown", "type": "Unclassified", "active": "Since Unknown"},
    "KillSec": {"origin": "Unknown", "type": "Hacktivist", "active": "Since Unknown"},
    "GhostSec": {"origin": "Unknown", "type": "Hacktivist", "active": "Since Unknown"},
    "Anonymous Sudan": {"origin": "Sudan (Disputed)", "type": "Hacktivist", "active": "2023"}
}

stats = stats.merge(
    pd.DataFrame.from_dict(ACTOR_META, orient="index").reset_index().rename(columns={"index": "actor"}),
    on="actor",
    how="left"
)

stats.fillna(
    {"origin": "Unknown", "type": "Unclassified", "active": "Since Unknown"},
    inplace=True
)

# -------------------------------------------------------------------
# FILTER BAR
# -------------------------------------------------------------------
f1, f2, f3, f4 = st.columns([2.5, 1.2, 1.2, 1.4])

with f1:
    search = st.text_input("Search Threat Actors", placeholder="Search by name, origin, or type...")

with f2:
    threat_level = st.selectbox("Threat Level", ["All", "Critical", "High"])

with f3:
    sort_by = st.selectbox("Sort By", ["Total Attacks", "Alphabetical"])

with f4:
    view_all = st.button("View All Actors", use_container_width=True)

# -------------------------------------------------------------------
# FILTER LOGIC
# -------------------------------------------------------------------
filtered = stats.copy()

if search:
    filtered = filtered[
        filtered["actor"].str.contains(search, case=False, na=False)
        | filtered["origin"].str.contains(search, case=False, na=False)
        | filtered["type"].str.contains(search, case=False, na=False)
    ]

if sort_by == "Total Attacks":
    filtered = filtered.sort_values("attacks", ascending=False)
else:
    filtered = filtered.sort_values("actor")

if not view_all:
    filtered = filtered.head(12)

# -------------------------------------------------------------------
# CARD GRID
# -------------------------------------------------------------------
cols = st.columns(4)
for i, row in filtered.iterrows():
    with cols[i % 4]:
        st.markdown(
            f"""
            <div style="
                background:{CARD_BG};
                border:1px solid {BORDER};
                border-radius:12px;
                padding:1.2rem;
                height:100%;
            ">
                <h3 style="margin-bottom:0.3rem;">{row.actor}</h3>
                <p style="color:{TEXT_MUTED}; font-size:0.85rem;">
                    Origin: {row.origin}<br>
                    Type: {row.type}<br>
                    Active: {row.active}
                </p>
                <div style="display:flex; justify-content:space-between; margin-top:1rem;">
                    <div><strong>{int(row.attacks)}</strong><br><span style="font-size:0.75rem;">Attacks</span></div>
                    <div><strong>{int(row.countries)}</strong><br><span style="font-size:0.75rem;">Countries</span></div>
                    <div><strong>{int(row.sectors)}</strong><br><span style="font-size:0.75rem;">Sectors</span></div>
                </div>
                <a href="/Actor_Profile?actor={row.actor}" target="_blank"
                   style="
                       display:block;
                       margin-top:1rem;
                       padding:0.6rem;
                       text-align:center;
                       background:{CYHAWK_RED};
                       color:white;
                       border-radius:6px;
                       text-decoration:none;
                       font-weight:600;
                   ">
                   View Profile
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )
