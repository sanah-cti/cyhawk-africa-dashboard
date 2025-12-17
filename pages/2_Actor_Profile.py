import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime

# ------------------------------------------------------------------
# Page config
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Threat Actor Profile | CyHawk Africa",
    page_icon="assets/favicon.ico",
    layout="wide"
)

# ------------------------------------------------------------------
# Secrets
# ------------------------------------------------------------------
OTX_API_KEY = st.secrets.get("ALIENVAULT_OTX_API_KEY")
RANSOMWARE_API_KEY = st.secrets.get("RANSOMWARE_LIVE_API_KEY")
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")

# ------------------------------------------------------------------
# Actor from URL
# ------------------------------------------------------------------
actor = st.query_params.get("actor")
if not actor:
    st.error("No threat actor specified.")
    st.stop()

# ------------------------------------------------------------------
# Load incidents data
# ------------------------------------------------------------------
@st.cache_data(ttl=3600)
def load_incidents():
    df = pd.read_csv("data/incidents.csv")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df.dropna(subset=["date"])

df = load_incidents()
actor_df = df[df["actor"] == actor]

# ------------------------------------------------------------------
# Internal analysis
# ------------------------------------------------------------------
internal_stats = {
    "total_attacks": len(actor_df),
    "high_severity": int((actor_df["severity"] == "High").sum()),
    "countries": actor_df["country"].value_counts().to_dict(),
    "industries": actor_df["sector"].value_counts().to_dict(),
}

# ------------------------------------------------------------------
# AlienVault OTX
# ------------------------------------------------------------------
@st.cache_data(ttl=86400)
def fetch_otx(actor_name):
    if not OTX_API_KEY:
        return {}

    headers = {"X-OTX-API-KEY": OTX_API_KEY}
    url = f"https://otx.alienvault.com/api/v1/search/pulses?q={actor_name}"
    r = requests.get(url, headers=headers, timeout=20)

    if r.status_code != 200:
        return {}

    pulses = r.json().get("results", [])
    iocs = {"ipv4": set(), "domain": set(), "hash": set()}

    for p in pulses:
        for ind in p.get("indicators", []):
            if ind["type"] in iocs:
                iocs[ind["type"]].add(ind["indicator"])

    return {
        "pulse_count": len(pulses),
        "iocs": {k: list(v)[:20] for k, v in iocs.items()}
    }

otx_data = fetch_otx(actor)

# ------------------------------------------------------------------
# ransomware.live
# ------------------------------------------------------------------
@st.cache_data(ttl=86400)
def fetch_ransomware(actor_name):
    if not RANSOMWARE_API_KEY:
        return {}

    headers = {"Authorization": f"Bearer {RANSOMWARE_API_KEY}"}
    url = f"https://api.ransomware.live/v1/group/{actor_name.lower()}"
    r = requests.get(url, headers=headers, timeout=20)

    if r.status_code != 200:
        return {}

    victims = r.json().get("victims", [])
    return {
        "victim_count": len(victims),
        "countries": list({v.get("country") for v in victims if v.get("country")}),
        "industries": list({v.get("sector") for v in victims if v.get("sector")}),
    }

ransomware_data = fetch_ransomware(actor)

# ------------------------------------------------------------------
# CyHawk blog index (example – extend this)
# ------------------------------------------------------------------
CYHAWK_POSTS = [
    {
        "title": "NightSpire Ransomware Targets Southern Africa",
        "url": "https://cyhawk-africa.com/nightspire-africa",
        "actors": ["Nightspire"],
        "date": "2025-06-12",
    }
]

blog_mentions = [p for p in CYHAWK_POSTS if actor in p["actors"]]

# ------------------------------------------------------------------
# LLM Analyst synthesis
# ------------------------------------------------------------------
@st.cache_data(ttl=86400)
def generate_report():
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = f"""
You are a cyber threat intelligence analyst.

Create a factual threat actor report for: {actor}

Use only the supplied data. Do not fabricate IOCs.

DATA:
Internal incidents: {internal_stats}
AlienVault OTX: {otx_data}
Ransomware.live: {ransomware_data}
CyHawk blog mentions: {blog_mentions}

Sections:
1. Overview
2. MITRE ATT&CK TTPs
3. Targeted Countries
4. Targeted Industries
5. Indicators of Compromise
6. Analyst Note
"""

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    return resp.choices[0].message.content

report_text = generate_report()

# ------------------------------------------------------------------
# UI – Header
# ------------------------------------------------------------------
st.image("assets/cyhawk_logo.png", width=140)

st.title(actor)
st.caption("Threat Actor Intelligence Report")

cols = st.columns(4)
cols[0].metric("Total Attacks", internal_stats["total_attacks"])
cols[1].metric("High Severity", internal_stats["high_severity"])
cols[2].metric("Countries", len(internal_stats["countries"]))
cols[3].metric("Sectors", len(internal_stats["industries"]))

st.divider()

# ------------------------------------------------------------------
# Overview + Analyst Report
# ------------------------------------------------------------------
st.subheader("Analyst Report")
st.write(report_text)

# ------------------------------------------------------------------
# Charts
# ------------------------------------------------------------------
if not actor_df.empty:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Targeted Countries")
        country_df = (
            actor_df["country"]
            .value_counts()
            .reset_index()
            .rename(columns={"index": "Country", "country": "Count"})
        )
        st.plotly_chart(
            px.bar(country_df, x="Count", y="Country", orientation="h"),
            use_container_width=True,
        )

    with col2:
        st.subheader("Targeted Industries")
        sector_df = (
            actor_df["sector"]
            .value_counts()
            .reset_index()
            .rename(columns={"index": "Sector", "sector": "Count"})
        )
        st.plotly_chart(
            px.pie(sector_df, names="Sector", values="Count", hole=0.4),
            use_container_width=True,
        )

# ------------------------------------------------------------------
# IOCs
# ------------------------------------------------------------------
st.subheader("Indicators of Compromise (OSINT)")

if otx_data.get("iocs"):
    for k, v in otx_data["iocs"].items():
        if v:
            st.markdown(f"**{k.upper()}**")
            for i in v:
                st.code(i)
else:
    st.info("No publicly available IOCs identified.")

st.warning(
    "IOCs are sourced from OSINT feeds and must be validated before operational use."
)

# ------------------------------------------------------------------
# Footer
# ------------------------------------------------------------------
st.caption(
    f"Last enriched: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} | CyHawk Africa"
)
