import streamlit as st
import pandas as pd
import urllib.parse
import os

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title="Threat Actors | CyHawk Africa",
    page_icon="🎯",
    layout="wide"
)

CYHAWK_RED = "#C41E3A"
CYHAWK_RED_DARK = "#9A1529"

# -------------------------------------------------
# Styles
# -------------------------------------------------
st.markdown(
    f"""
    <style>
    .page-header {{
        background: linear-gradient(135deg, {CYHAWK_RED}, {CYHAWK_RED_DARK});
        padding: 3rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }}
    .actor-card {{
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 10px;
        padding: 1.25rem;
        height: 100%;
    }}
    .actor-badge {{
        background: {CYHAWK_RED};
        color: white;
        padding: 0.25rem 0.6rem;
        border-radius: 10px;
        font-size: 0.65rem;
        font-weight: 700;
    }}
    .view-btn {{
        display:block;
        margin-top:1rem;
        padding:0.6rem;
        text-align:center;
        background:{CYHAWK_RED};
        color:white;
        border-radius:6px;
        text-decoration:none;
        font-weight:600;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# Header
# -------------------------------------------------
st.markdown(
    """
    <div class="page-header">
        <h1>Threat Actor Intelligence</h1>
        <p>Comprehensive profiles of active threat actors targeting African organizations</p>
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# Load + prepare data
# -------------------------------------------------
@st.cache_data
def load_data():
    path = "data/incidents.csv"
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path)
    df["actor"] = df["actor"].fillna("Unknown").astype(str)
    return df

df = load_data()

if df.empty:
    st.warning("No threat actor data available.")
    st.stop()

# Aggregate and deduplicate
actor_stats = (
    df.groupby("actor", as_index=False)
    .size()
    .rename(columns={"size": "total_attacks"})
    .sort_values("total_attacks", ascending=False)
    .head(12)  # GUARANTEED 12
)

# -------------------------------------------------
# Render cards in rows of 4
# -------------------------------------------------
actors = actor_stats.to_dict("records")

for i in range(0, len(actors), 4):
    cols = st.columns(4, gap="medium")

    for col, actor in zip(cols, actors[i:i + 4]):
        actor_name = actor["actor"]
        attacks = int(actor["total_attacks"])
        slug = urllib.parse.quote_plus(actor_name.lower().replace(" ", "-"))

        with col:
            st.markdown(
                f"""
                <div class="actor-card">
                    <div style="display:flex; justify-content:space-between;">
                        <h3 style="margin:0;">{actor_name}</h3>
                        <span class="actor-badge">ACTIVE</span>
                    </div>

                    <p style="color:#8B949E; font-size:0.85rem; margin-top:0.5rem;">
                        Total Attacks Tracked
                    </p>

                    <h2 style="margin-top:0;">{attacks}</h2>

                    <a class="view-btn"
                       href="/Actor_Profile?actor={slug}"
                       target="_blank">
                        View Profile →
                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )

# -------------------------------------------------
# Footer
# -------------------------------------------------
st.markdown(
    """
    <hr>
    <p style="color:#8B949E; font-size:0.8rem;">
        © CyHawk Africa — Threat Intelligence Platform
    </p>
    """,
    unsafe_allow_html=True
)
