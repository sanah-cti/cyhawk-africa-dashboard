import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
import os
import random
from datetime import timedelta
import base64
from urllib.parse import unquote

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="CyHawk Africa | Threat Actor Profile",
    page_icon="assets/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# THEME STATE
# --------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

# --------------------------------------------------
# COLORS
# --------------------------------------------------
CYHAWK_RED = "#C41E3A"
CYHAWK_RED_DARK = "#9A1529"

def theme_config():
    return {
        "bg": "#0D1117",
        "bg_secondary": "#161B22",
        "card": "#1C2128",
        "card_hover": "#22272E",
        "border": "#30363D",
        "text": "#E6EDF3",
        "text_secondary": "#8B949E",
        "text_muted": "#6E7681",
        "accent": CYHAWK_RED,
        "success": "#238636",
        "warning": "#9E6A03",
        "danger": "#DA3633",
        "template": "plotly_dark"
    }

C = theme_config()

# --------------------------------------------------
# CSS (UNCHANGED STRUCTURE)
# --------------------------------------------------
st.markdown(f"""
<style>
* {{
    font-family: Inter, sans-serif;
}}
.stApp {{
    background: {C['bg']};
}}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------
def generate_sample_data():
    actors = [
        "Keymous Plus",
        "Nightspire",
        "b4bayega",
        "BigBrother",
        "Anonymous Sudan",
        "Dark Hell 07x"
    ]
    countries = ["Nigeria", "South Africa", "Kenya", "Egypt", "Morocco"]
    threat_types = [
        "Hacktivism",
        "Ransomware",
        "Database Breach",
        "Initial Access Broker",
        "DDoS"
    ]
    sectors = ["Government", "Finance", "Telecoms", "Healthcare"]
    severities = ["High", "Medium", "Low"]

    data = []
    start = datetime(2024, 1, 1)

    for _ in range(180):
        data.append({
            "date": start + timedelta(days=random.randint(0, 400)),
            "actor": random.choice(actors),
            "country": random.choice(countries),
            "threat_type": random.choice(threat_types),
            "sector": random.choice(sectors),
            "severity": random.choice(severities),
            "source": "OSINT"
        })
    return pd.DataFrame(data)

@st.cache_data
def load_data():
    if os.path.exists("data/incidents.csv"):
        df = pd.read_csv("data/incidents.csv")
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
    else:
        df = generate_sample_data()

    for col in ["actor", "country", "threat_type", "sector", "severity"]:
        df[col] = df[col].fillna("Unknown").astype(str)

    return df

df = load_data()

# --------------------------------------------------
# ACTOR RESOLUTION (CRITICAL FIX)
# --------------------------------------------------
actor = None

if "actor" in st.query_params:
    actor = st.query_params.get("actor")
    if isinstance(actor, list):
        actor = actor[0]
    actor = unquote(actor).strip()

if not actor:
    actor = st.session_state.get("selected_actor")

if not actor:
    st.error("No threat actor selected.")
    st.stop()

actor_df = df[df["actor"].str.lower() == actor.lower()]

# --------------------------------------------------
# THREAT TYPE CLASSIFICATION (AUTHORITATIVE)
# --------------------------------------------------
ACTOR_TYPES = {
    "Keymous Plus": "Hacktivist Group",
    "Anonymous Sudan": "Hacktivist Group",
    "Nightspire": "Ransomware Group",
    "Dark Hell 07x": "Ransomware Group",
    "b4bayega": "Database Breach Actor",
    "BigBrother": "Initial Access Broker (IAB)"
}

actor_type = ACTOR_TYPES.get(actor, "Unclassified Threat Actor")

# --------------------------------------------------
# MITRE ATT&CK MAPPING BY TYPE
# --------------------------------------------------
MITRE_BY_TYPE = {
    "Hacktivist Group": [
        "T1499 – Endpoint Denial of Service",
        "T1565 – Data Manipulation",
        "T1071 – Application Layer Protocol"
    ],
    "Ransomware Group": [
        "T1486 – Data Encrypted for Impact",
        "T1078 – Valid Accounts",
        "T1021 – Remote Services"
    ],
    "Initial Access Broker (IAB)": [
        "T1078 – Valid Accounts",
        "T1190 – Exploit Public-Facing Application",
        "T1133 – External Remote Services"
    ],
    "Database Breach Actor": [
        "T1190 – Exploit Public-Facing Application",
        "T1046 – Network Service Scanning",
        "T1552 – Unsecured Credentials"
    ]
}

mitre_ttps = MITRE_BY_TYPE.get(actor_type, [])

# --------------------------------------------------
# EXECUTIVE SUMMARY (STRATEGIC, DATA-DRIVEN)
# --------------------------------------------------
total_attacks = len(actor_df)
countries = actor_df["country"].nunique()
sectors = actor_df["sector"].nunique()

executive_summary = f"""
**{actor}** is assessed as a **{actor_type}** based on observed activity patterns, operational focus, and targeting behavior.

The actor has been linked to **{total_attacks} documented incidents**, impacting **{countries} countries** and **{sectors} industry sectors**.  
Activity suggests {'regional influence operations' if actor_type == 'Hacktivist Group' else 'financially motivated operations'} with a sustained operational tempo.

The threat actor demonstrates repeatable tradecraft and should be considered an **active threat** within the African cyber threat landscape.
"""

# --------------------------------------------------
# HEADER (UNCHANGED STRUCTURE)
# --------------------------------------------------
st.markdown(f"""
<div style="background: linear-gradient(135deg, {CYHAWK_RED}, {CYHAWK_RED_DARK});
            padding:2rem;border-radius:12px;color:white;">
    <h1>{actor}</h1>
    <p>{actor_type}</p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# OVERVIEW
# --------------------------------------------------
st.subheader("📋 Executive Summary")
st.markdown(executive_summary)

# --------------------------------------------------
# ATTACK STATISTICS
# --------------------------------------------------
st.subheader("📊 Attack Statistics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Attacks", total_attacks)
with col2:
    st.metric("Countries", countries)
with col3:
    st.metric("Industries", sectors)
with col4:
    st.metric("High Severity", len(actor_df[actor_df["severity"] == "High"]))

# --------------------------------------------------
# MITRE ATT&CK
# --------------------------------------------------
st.subheader("🎯 MITRE ATT&CK Mapping")
if mitre_ttps:
    for ttp in mitre_ttps:
        st.markdown(f"- {ttp}")
else:
    st.info("No ATT&CK mapping available for this actor type.")

# --------------------------------------------------
# TARGETED COUNTRIES
# --------------------------------------------------
if not actor_df.empty:
    country_stats = actor_df["country"].value_counts().reset_index()
    country_stats.columns = ["Country", "Incidents"]

    fig = px.bar(
        country_stats,
        x="Incidents",
        y="Country",
        orientation="h",
        template=C["template"],
        color="Incidents",
        color_continuous_scale=[[0, C["card"]], [1, C["accent"]]]
    )
    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# TARGETED INDUSTRIES
# --------------------------------------------------
sector_stats = actor_df["sector"].value_counts().reset_index()
sector_stats.columns = ["Sector", "Incidents"]

fig = px.pie(
    sector_stats,
    values="Incidents",
    names="Sector",
    hole=0.4,
    template=C["template"]
)
st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# ANALYST ASSESSMENT
# --------------------------------------------------
st.subheader("💼 Analyst Assessment")
st.markdown(f"""
**Threat Outlook:** Elevated  
**Confidence Level:** Medium–High  

Organizations operating in affected sectors should prioritize:
1. Proactive monitoring aligned to observed TTPs  
2. Credential hygiene and access control reviews  
3. Preparedness for escalation or secondary access resale  

This actor remains relevant and should be continuously tracked.
""")

st.success("Threat actor profile generated successfully.")
