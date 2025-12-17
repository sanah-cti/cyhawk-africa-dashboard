import streamlit as st
import pandas as pd
from datetime import datetime
import os

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Threat Actor Intelligence | CyHawk Africa",
    page_icon="🎯",
    layout="wide"
)

BASE_URL = "https://cyhawk-africa-dashboard.streamlit.app/Threat_Actors"

# -----------------------------
# SEO / CANONICAL METADATA
# -----------------------------
st.markdown(f"""
<link rel="canonical" href="{BASE_URL}" />

<meta name="description" content="Threat Actor Intelligence by CyHawk Africa. Comprehensive profiles of cyber threat actors targeting African organizations." />

<meta property="og:title" content="Threat Actor Intelligence | CyHawk Africa" />
<meta property="og:description" content="Explore detailed profiles of active cyber threat actors targeting Africa." />
<meta property="og:url" content="{BASE_URL}" />
<meta property="og:type" content="website" />
<meta property="og:site_name" content="CyHawk Africa" />

<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Threat Actor Intelligence | CyHawk Africa" />
<meta name="twitter:description" content="Profiles of active cyber threat actors impacting African organizations." />
""", unsafe_allow_html=True)

# -----------------------------
# THEME
# -----------------------------
CYHAWK_RED = "#C41E3A"
CYHAWK_RED_DARK = "#9A1529"

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

C = {
    "bg": "#0D1117",
    "card": "#161B22",
    "border": "#30363D",
    "text": "#E6EDF3",
    "muted": "#8B949E",
    "accent": CYHAWK_RED
}

# -----------------------------
# STYLES
# -----------------------------
st.markdown(f"""
<style>
* {{ font-family: Inter, sans-serif; }}
.stApp {{ background:{C['bg']}; }}

.page-header {{
    background: linear-gradient(135deg, {CYHAWK_RED} 0%, {CYHAWK_RED_DARK} 100%);
    padding:3rem;
    border-radius:14px;
    text-align:center;
    margin-bottom:2rem;
}}

.page-title {{
    color:white;
    font-size:2.6rem;
    font-weight:700;
}}

.page-subtitle {{
    color:rgba(255,255,255,0.9);
    margin-top:.5rem;
}}

.actor-card {{
    background:{C['card']};
    border:1px solid {C['border']};
    border-radius:12px;
    padding:1.25rem;
    height:100%;
}}

.actor-name {{
    font-size:1.15rem;
    font-weight:700;
    color:{C['text']};
}}

.badge {{
    background:{C['accent']};
    color:white;
    font-size:0.65rem;
    padding:.25rem .6rem;
    border-radius:10px;
    font-weight:700;
}}

.view-btn {{
    display:block;
    text-align:center;
    padding:.6rem;
    background:{C['accent']};
    color:white;
    border-radius:6px;
    text-decoration:none;
    font-weight:600;
    margin-top:1rem;
}}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# DATA
# -----------------------------
@st.cache_data
def load_data():
    if not os.path.exists("data/incidents.csv"):
