import streamlit as st
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# ----------------------------------------------------
# Page Config
# ----------------------------------------------------
st.set_page_config(
    page_title="Threat Actors | CyHawk Africa",
    page_icon="🎯",
    layout="wide"
)

# ----------------------------------------------------
# Theme + Constants
# ----------------------------------------------------
CYHAWK_RED = "#C41E3A"
CYHAWK_RED_DARK = "#9A1529"

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def theme():
    return {
        "bg": "#0D1117",
        "card": "#161B22",
        "border": "#30363D",
        "text": "#E6EDF3",
        "muted": "#8B949E",
        "accent": CYHAWK_RED
    }

C = theme()

# ----------------------------------------------------
# JSON-LD (Google Structured Data)
# ----------------------------------------------------
def inject_jsonld():
    jsonld = """
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "WebPage",
      "name": "Threat Actor Intelligence | CyHawk Africa",
      "description": "Profiles of cyber threat actors targeting African organizations.",
      "publisher": {
        "@type": "Organization",
        "name": "CyHawk Africa",
        "url": "https://cyhawk-africa.com"
      }
    }
    </script>
    """
    st.components.v1.html(jsonld, height=0)

inject_jsonld()

# ----------------------------------------------------
# CSS
# ----------------------------------------------------
st.markdown(
    f"""
    <style>
    .main {{
        background-color: {C['bg']};
    }}
    .page-header {{
        background: linear-gradient(135deg, {CYHAWK_RED}, {CYHAWK_RED_DARK});
        padding: 3rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
    }}
    .page-title {{
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
    }}
    .card {{
        background: {C['card']};
        border: 1px solid {C['border']};
        border-radius: 10px;
        padding: 1.25rem;
        height: 100%;
    }}
    .badge {{
        background: {CYHAWK_RED};
        color: white;
        padding: 0.25rem 0.6rem;
        border-radius: 12px;
        font-size: 0.65rem;
        font-weight: 700;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------------------------------
# Header
# ----------------------------------------------------
st.markdown(
    """
    <div class="page-header">
        <div class="page-title">Threat Actor Intelligence</div>
        <p style="color: rgba(255,255,255,0.9);">
            Comprehensive profiles of active threat actors targeting African organizations
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ----------------------------------------------------
# Load Data
# ----------------------------------------------------
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

# ----------------------------------------------------
# Actor Stats
# ----------------------------------------------------
stats = (
    df.groupby("actor")
    .size()
    .reset_index(name="total_attacks")
    .sort_values("total_attacks", ascending=False)
)

# ----------------------------------------------------
# Display Cards
# ----------------------------------------------------
cols = st.columns(4, gap="medium")

for idx, row in stats.head(12).iterrows():
    actor_name = row["actor"]
    actor_slug = urllib.parse.quote_plus(actor_name.lower().replace(" ", "-"))

    with cols[idx % 4]:
        st.markdown(
            f"""
            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:start;">
                    <h3 style="margin:0;">{actor_name}</h3>
                    <span class="badge">ACTIVE</span>
                </div>

                <p style="color:{C['muted']}; font-size:0.85rem;">
                    Total Attacks Tracked
                </p>

                <h2 style="margin-top:0;">{row['total_attacks']}</h2>

                <a href="/Actor_Profile?actor={actor_slug}" target="_blank"
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
                   View Profile →
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )

# ----------------------------------------------------
# Footer
# ----------------------------------------------------
st.markdown(
    f"""
    <hr>
    <p style="color:{C['muted']}; font-size:0.8rem;">
        © {datetime.utcnow().year} CyHawk Africa · Threat Intelligence Platform
    </p>
    """,
    unsafe_allow_html=True
)
