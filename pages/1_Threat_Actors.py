import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Threat Actor Intelligence | CyHawk Africa",
    page_icon="assets/favicon.ico",
    layout="wide"
)

# ---------------------------------------------------------
# THEME
# ---------------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

CYHAWK_RED = "#C41E3A"

def theme():
    return {
        "bg": "#0D1117",
        "card": "#161B22",
        "border": "#30363D",
        "text": "#E6EDF3",
        "muted": "#8B949E",
        "critical": "#DA3633"
    }

T = theme()

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
h1, h2 = st.columns([1, 6])
with h1:
    st.image("assets/cyhawk_logo.png", width=90)

with h2:
    st.markdown("## Threat Actor Intelligence")
    st.caption(
        "Comprehensive profiles of active threat actors targeting African organizations"
    )

st.divider()

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
@st.cache_data
def load_data():
    if os.path.exists("data/incidents.csv"):
        df = pd.read_csv("data/incidents.csv")
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
        return df
    return pd.DataFrame()

df = load_data()

# ---------------------------------------------------------
# AGGREGATE ACTOR STATS
# ---------------------------------------------------------
actor_stats = (
    df.groupby("actor")
    .agg(
        total_attacks=("date", "count"),
        countries=("country", "nunique"),
        sectors=("sector", "nunique"),
        high_severity=("severity", lambda x: (x == "High").sum())
    )
    .reset_index()
)

# ---------------------------------------------------------
# THREAT LEVEL LOGIC
# ---------------------------------------------------------
def threat_level(row):
    if row["total_attacks"] > 50 or row["high_severity"] > 10:
        return "Critical"
    return "High"

actor_stats["threat_level"] = actor_stats.apply(threat_level, axis=1)

# ---------------------------------------------------------
# STATIC PROFILE METADATA (EXTENDABLE)
# ---------------------------------------------------------
profiles = {
    "Keymous Plus": {"origin": "Unknown", "type": "Unclassified", "active": "Unknown"},
    "OurSec": {"origin": "Unknown", "type": "Unclassified", "active": "Unknown"},
    "Funksec": {"origin": "Unknown", "type": "Unclassified", "active": "Unknown"},
    "dark hell 07x": {"origin": "Unknown", "type": "Unclassified", "active": "Unknown"},
    "FireWire": {"origin": "Unknown", "type": "Unclassified", "active": "Unknown"},
    "Devman": {"origin": "Unknown", "type": "Unclassified", "active": "Unknown"},
    "SKYZZXPLOIT": {"origin": "Unknown", "type": "Unclassified", "active": "Unknown"},
    "hider_nex": {"origin": "Unknown", "type": "Unclassified", "active": "Unknown"},
    "Nightspire": {"origin": "Unknown", "type": "Unclassified", "active": "Unknown"},
    "OurSec2": {"origin": "Unknown", "type": "Unclassified", "active": "Unknown"},
    "FireWireX": {"origin": "Unknown", "type": "Unclassified", "active": "Unknown"},
    "DarkOps": {"origin": "Unknown", "type": "Unclassified", "active": "Unknown"},
}

# ---------------------------------------------------------
# FILTER BAR
# ---------------------------------------------------------
f1, f2, f3, f4 = st.columns([4, 2, 2, 2])

with f1:
    search = st.text_input("Search Threat Actors", placeholder="Search by name...")

with f2:
    level_filter = st.selectbox("Threat Level", ["All", "Critical", "High"])

with f3:
    sort_by = st.selectbox("Sort By", ["Total Attacks", "Alphabetical"])

with f4:
    st.markdown("<br>", unsafe_allow_html=True)
    view_all = st.button("View All Actors", use_container_width=True, type="primary")

# ---------------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------------
filtered = actor_stats.copy()

if search:
    filtered = filtered[filtered["actor"].str.contains(search, case=False)]

if level_filter != "All":
    filtered = filtered[filtered["threat_level"] == level_filter]

if sort_by == "Total Attacks":
    filtered = filtered.sort_values("total_attacks", ascending=False)
else:
    filtered = filtered.sort_values("actor")

if not view_all:
    filtered = filtered.head(12)

# ---------------------------------------------------------
# ACTOR CARD RENDERER
# ---------------------------------------------------------
def actor_card(actor):
    meta = profiles.get(actor["actor"], {})
    with st.container(border=True):
        st.markdown(
            f"### {actor['actor']} "
            f"<span style='background:{T['critical']}; color:white; "
            f"padding:4px 8px; border-radius:6px; font-size:12px;'>"
            f"{actor['threat_level']}</span>",
            unsafe_allow_html=True
        )

        st.caption("Unknown")

        st.markdown(
            f"""
            **Origin:** {meta.get("origin", "Unknown")}  
            **Type:** {meta.get("type", "Unclassified")}  
            **Active:** Since {meta.get("active", "Unknown")}
            """
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Attacks", int(actor["total_attacks"]))
        c2.metric("Countries", int(actor["countries"]))
        c3.metric("Sectors", int(actor["sectors"]))

        profile_url = f"/Actor_Profile?actor={actor['actor']}"
        st.link_button(
            "View Profile",
            profile_url,
            use_container_width=True
        )

# ---------------------------------------------------------
# GRID DISPLAY (4 x 3)
# ---------------------------------------------------------
for i in range(0, len(filtered), 4):
    cols = st.columns(4)
    for col, (_, row) in zip(cols, filtered.iloc[i:i+4].iterrows()):
        with col:
            actor_card(row)

# ---------------------------------------------------------
# FOOTER STATS
# ---------------------------------------------------------
st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("Total Threat Actors", actor_stats["actor"].nunique())
c2.metric("Critical Actors", (actor_stats["threat_level"] == "Critical").sum())
c3.metric("Total Attacks Tracked", actor_stats["total_attacks"].sum())
