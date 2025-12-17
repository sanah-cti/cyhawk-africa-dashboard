"""
Comprehensive Threat Actor Profile Generator
Data Sources:
1. incidents.csv (primary ground truth)
2. AlienVault OTX (community threat intel, IOCs, tags)
3. ransomware.live (victim confirmation)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import os
from datetime import datetime

# -----------------------------------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Actor Profile | CyHawk Africa",
    page_icon="assets/favicon.ico",
    layout="wide"
)

CYHAWK_RED = "#C41E3A"
CYHAWK_RED_DARK = "#9A1529"

# -----------------------------------------------------------------------------
# MITRE ATT&CK MAPPING (CONTROLLED, ANALYST-SAFE)
# -----------------------------------------------------------------------------
MITRE_TTP_MAPPING = {
    "ransomware": ("T1486", "Data Encrypted for Impact", "Impact"),
    "ddos": ("T1499", "Endpoint Denial of Service", "Impact"),
    "phishing": ("T1566", "Phishing", "Initial Access"),
    "credential": ("T1555", "Credentials from Password Stores", "Credential Access"),
    "lateral": ("T1021", "Remote Services", "Lateral Movement"),
    "c2": ("T1071", "Application Layer Protocol", "Command and Control"),
    "exfiltration": ("T1041", "Exfiltration Over C2 Channel", "Exfiltration"),
    "malware": ("T1204", "User Execution", "Execution"),
}

# -----------------------------------------------------------------------------
# DATA LOADING
# -----------------------------------------------------------------------------
@st.cache_data
def load_incidents():
    if not os.path.exists("data/incidents.csv"):
        return pd.DataFrame()
    df = pd.read_csv("data/incidents.csv")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df.dropna(subset=["date"])

df = load_incidents()

# -----------------------------------------------------------------------------
# API FETCHERS
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_otx(actor):
    """
    Safely fetch AlienVault OTX intelligence.
    Degrades gracefully on timeout or rate limiting.
    """
    api_key = st.secrets.get("ALIENVAULT_OTX_API_KEY", None)

    if not api_key:
        return {
            "available": False,
            "error": "OTX API key not configured",
            "pulses": [],
            "tags": [],
            "iocs": []
        }

    url = "https://otx.alienvault.com/api/v1/search/pulses"
    headers = {"X-OTX-API-KEY": api_key}

    try:
        response = requests.get(
            url,
            headers=headers,
            params={"q": actor, "limit": 20},
            timeout=8  # reduced timeout for Streamlit Cloud
        )

        if response.status_code != 200:
            return {
                "available": False,
                "error": f"OTX returned {response.status_code}",
                "pulses": [],
                "tags": [],
                "iocs": []
            }

        data = response.json()
        pulses = data.get("results", [])

        tags = set()
        iocs = []

        for pulse in pulses:
            tags.update(pulse.get("tags", []))
            for ind in pulse.get("indicators", []):
                iocs.append((ind.get("type"), ind.get("indicator")))

        return {
            "available": True,
            "pulses": pulses,
            "tags": list(tags),
            "iocs": iocs
        }

    except requests.exceptions.Timeout:
        return {
            "available": False,
            "error": "AlienVault OTX timeout",
            "pulses": [],
            "tags": [],
            "iocs": []
        }

    except Exception as e:
        return {
            "available": False,
            "error": str(e),
            "pulses": [],
            "tags": [],
            "iocs": []
        }

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_ransomware_live_data(group):
    """
    Fetch comprehensive ransomware.live intelligence for a threat actor.
    Gracefully degrades if endpoints are unavailable.
    """
    base = "https://api.ransomware.live"
    data = {
        "available": False,
        "group": group,
        "profile": None,
        "iocs": [],
        "negotiations": [],
        "ransom_notes": [],
        "yara_rules": []
    }

    try:
        # Normalize group name
        group_clean = group.lower().replace(" ", "").replace("-", "")

        endpoints = {
            "profile": f"{base}/groups/{group_clean}",
            "iocs": f"{base}/iocs/{group_clean}",
            "negotiations": f"{base}/negotiations/{group_clean}",
            "ransomnotes": f"{base}/ransomnotes/{group_clean}",
            "yara": f"{base}/yara/{group_clean}",
        }

        for key, url in endpoints.items():
            try:
                r = requests.get(url, timeout=8)
                if r.status_code == 200:
                    data[key if key != "ransomnotes" else "ransom_notes"] = r.json()
            except requests.exceptions.Timeout:
                continue

        # Determine availability
        if any([
            data["profile"],
            data["iocs"],
            data["negotiations"],
            data["ransom_notes"],
            data["yara_rules"]
        ]):
            data["available"] = True

        return data

    except Exception as e:
        data["error"] = str(e)
        return data

# -----------------------------------------------------------------------------
# ATT&CK EXTRACTION
# -----------------------------------------------------------------------------
def extract_ttps(actor_df, otx):
    keywords = set()

    for col in ["threat_type", "source"]:
        if col in actor_df.columns:
            keywords.update(actor_df[col].dropna().str.lower())

    if otx:
        keywords.update([t.lower() for t in otx["tags"]])

    mapped = {}
    for k in keywords:
        for key, val in MITRE_TTP_MAPPING.items():
            if key in k:
                mapped[val[0]] = {
                    "id": val[0],
                    "name": val[1],
                    "tactic": val[2]
                }

    return list(mapped.values())

# -----------------------------------------------------------------------------
# ACTOR SELECTION
# -----------------------------------------------------------------------------
actor = st.query_params.get("actor", "")
if isinstance(actor, list):
    actor = actor[0]

if not actor:
    st.error("No threat actor selected.")
    st.stop()

actor_df = df[df["actor"] == actor]

# -----------------------------------------------------------------------------
# PROFILE METRICS
# -----------------------------------------------------------------------------
total_attacks = len(actor_df)
countries = actor_df["country"].nunique()
sectors = actor_df["sector"].nunique()
high_sev = len(actor_df[actor_df["severity"] == "High"]) if "severity" in actor_df else 0

threat_level = "Medium"
if total_attacks > 20 or high_sev > 5:
    threat_level = "High"
if total_attacks > 50 or high_sev > 15:
    threat_level = "Critical"

# -----------------------------------------------------------------------------
# API DATA
# -----------------------------------------------------------------------------
otx = fetch_otx(actor)
ransomware = fetch_ransomware_live_data(actor)
ttps = extract_ttps(actor_df, otx)

# -----------------------------------------------------------------------------
# HEADER
# -----------------------------------------------------------------------------
st.markdown(f"""
<div style="background:linear-gradient(135deg,{CYHAWK_RED},{CYHAWK_RED_DARK});
padding:2.5rem;border-radius:12px;color:white;">
<a href="/Threat_Actors" style="color:white;text-decoration:none;">← Back</a>
<h1>{actor}</h1>
<p>Threat Level: <strong>{threat_level}</strong></p>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# OVERVIEW
# -----------------------------------------------------------------------------
st.markdown("## 📋 Overview")
st.markdown(
    f"**{actor}** has been linked to **{total_attacks} incidents** "
    f"across **{countries} countries** and **{sectors} sectors**. "
    "Analysis combines CyHawk incident tracking with external intelligence sources."
)

if ransomware:
    st.markdown(f"Ransomware.live confirms **{len(ransomware)} victim disclosures**.")

if otx:
    st.markdown(f"AlienVault OTX references **{len(otx['pulses'])} intelligence pulses**.")

# -----------------------------------------------------------------------------
# ATTACK STATISTICS
# -----------------------------------------------------------------------------
st.markdown("## 📊 Attack Statistics")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Attacks", total_attacks)
c2.metric("Countries", countries)
c3.metric("Sectors", sectors)
c4.metric("High Severity", high_sev)

# -----------------------------------------------------------------------------
# TARGETED COUNTRIES
# -----------------------------------------------------------------------------
st.markdown("## 🌍 Targeted Countries")
country_df = actor_df["country"].value_counts().head(10).reset_index()
country_df.columns = ["Country", "Incidents"]

fig = px.bar(country_df, x="Incidents", y="Country", orientation="h")
fig.update_traces(marker_color=CYHAWK_RED)
st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------------------
# TARGETED INDUSTRIES
# -----------------------------------------------------------------------------
st.markdown("## 🏢 Targeted Industries")
sector_df = actor_df["sector"].value_counts().reset_index()
sector_df.columns = ["Sector", "Incidents"]

fig = px.pie(sector_df, values="Incidents", names="Sector", hole=0.4)
st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------------------
# MITRE ATT&CK
# -----------------------------------------------------------------------------
st.markdown("## 🎯 Observed ATT&CK Techniques")

if ttps:
    for t in ttps:
        st.markdown(f"**{t['id']} – {t['name']}**  \n*Tactic:* {t['tactic']}")
else:
    st.info("No ATT&CK techniques confidently mapped at this time.")

# -----------------------------------------------------------------------------
# IOCs
# -----------------------------------------------------------------------------
if otx and otx["iocs"]:
    st.markdown("## 🔍 Indicators of Compromise")
    for t, v in otx["iocs"][:50]:
        st.code(f"{t}: {v}")

# -----------------------------------------------------------------------------
# RANSOMWARE VICTIMS
# -----------------------------------------------------------------------------
if ransomware:
    st.markdown("## 🎯 Ransomware Victims")
    if ransomware:
    if ransomware.get("negotiations"):
        for n in ransomware["negotiations"][:20]:
            ...

    if ransomware.get("iocs"):
        for ioc in ransomware["iocs"][:50]:
            ...

    if ransomware.get("ransomnotes"):
        for note in ransomware["ransomnotes"][:10]:
            ...

    if ransomware.get("yara"):
        for rule in ransomware["yara"][:10]:
            ...

# -----------------------------------------------------------------------------
# TIMELINE
# -----------------------------------------------------------------------------
st.markdown("## 📈 Activity Timeline")
timeline = actor_df.groupby(actor_df["date"].dt.to_period("M")).size().reset_index()
timeline.columns = ["Month", "Incidents"]
timeline["Month"] = timeline["Month"].dt.to_timestamp()

fig = px.line(timeline, x="Month", y="Incidents")
fig.update_traces(line_color=CYHAWK_RED)
st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------------------
# ANALYST NOTE
# -----------------------------------------------------------------------------
st.markdown("## 💼 Analyst Assessment")
st.markdown(
    f"Based on multi-source intelligence, **{actor}** demonstrates "
    f"{'high operational maturity' if threat_level != 'Medium' else 'emerging activity'}. "
    "Defenders should prioritize monitoring aligned ATT&CK techniques and apply "
    "IOC-driven detection controls."
)

st.success("Threat actor profile generated successfully.")
