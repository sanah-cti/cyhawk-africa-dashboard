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

# -------------------------------------------------
# Header (native)
# -------------------------------------------------
st.markdown(
    """
    <style>
    .header {
        background: linear-gradient(135deg, #C41E3A, #9A1529);
        padding: 3rem;
        border-radius: 14px;
        text-align: center;
        margin-bottom: 2rem;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="header">
        <h1>Threat Actor Intelligence</h1>
        <p>Comprehensive profiles of active threat actors targeting African organizations</p>
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# Load data
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

# -------------------------------------------------
# Aggregate actors (top 12, deduped)
# -------------------------------------------------
actor_stats = (
    df.groupby("actor", as_index=False)
    .size()
    .rename(columns={"size": "total_attacks"})
    .sort_values("total_attacks", ascending=False)
    .head(12)
)

actors = actor_stats.to_dict("records")

# -------------------------------------------------
# Render cards — STREAMLIT NATIVE ONLY
# -------------------------------------------------
for i in range(0, len(actors), 4):
    cols = st.columns(4, gap="medium")

    for col, actor in zip(cols, actors[i:i + 4]):
        actor_name = actor["actor"]
        attacks = int(actor["total_attacks"])
        slug = urllib.parse.quote_plus(actor_name.lower().replace(" ", "-"))

        with col:
            with st.container(border=True):

                # Header row
                hcol1, hcol2 = st.columns([4, 1])
                with hcol1:
                    st.subheader(actor_name)
                with hcol2:
                    st.markdown(
                        f"<span style='background:{CYHAWK_RED}; color:white; padding:0.25rem 0.6rem; border-radius:10px; font-size:0.7rem;'>ACTIVE</span>",
                        unsafe_allow_html=True
                    )

                # Metrics
                st.caption("Total Attacks Tracked")
                st.metric(label="", value=attacks)

                # CTA — native link button (new tab)
                st.link_button(
                    "View Profile →",
                    url=f"/Actor_Profile?actor={slug}",
                    use_container_width=True
                )

# -------------------------------------------------
# Footer
# -------------------------------------------------
st.divider()
st.caption("© CyHawk Africa — Threat Intelligence Platform")
