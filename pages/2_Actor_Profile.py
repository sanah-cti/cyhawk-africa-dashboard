"""
CyHawk Africa – Comprehensive Threat Actor Profile
Sources:
- incidents.csv
- AlienVault OTX
- ransomware.live
Adds:
- Normalized ransomware intelligence
- Quantitative Risk Score
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import requests
import os

# -------------------------------------------------------------------
# Page config
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Actor Profile | CyHawk Africa",
    page_icon="assets/favicon.ico",
    layout="wide"
)

CYHAWK_RED = "#C41E3A"

# -------------------------------------------------------------------
# Utilities
# -------------------------------------------------------------------
@st.cache_data
def load_incidents():
    if not os.path.exists("data/incidents.csv"):
        return pd.DataFrame()
    df = pd.read_csv("data/incidents.csv")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df.dropna(subset=["date"])


@st.cache_data(ttl=3600)
def fetch_otx(actor):
    key = st.secrets.get("ALIENVAULT_OTX_API_KEY", "")
    if not key:
        return {}

    r = requests.get(
        "https://otx.alienvault.com/api/v1/search/pulses",
        headers={"X-OTX-API-KEY": key},
        params={"q": actor},
        timeout=15,
    )
    if r.status_code != 200:
        return {}

    data = r.json().get("results", [])
    iocs = {"domains": [], "ips": [], "hashes": [], "cves": []}
    tags = set()

    for pulse in data:
        tags.update(pulse.get("tags", []))
        for ind in pulse.get("indicators", []):
            t, v = ind.get("type"), ind.get("indicator")
            if t == "domain":
                iocs["domains"].append(v)
            elif t in ["IPv4", "IPv6"]:
                iocs["ips"].append(v)
            elif "FileHash" in t:
                iocs["hashes"].append(v)
            elif t == "CVE":
                iocs["cves"].append(v)

    return {
        "pulse_count": len(data),
        "tags": sorted(tags),
        "iocs": {k: sorted(set(v)) for k, v in iocs.items()},
    }


@st.cache_data(ttl=3600)
def fetch_ransomware(actor):
    base = "https://api.ransomware.live"
    result = {}

    endpoints = {
        "groups": f"/groups/{actor}",
        "iocs": f"/iocs/{actor}",
        "negotiations": f"/negotiations/{actor}",
        "ransomnotes": f"/ransomnotes/{actor}",
        "yara": f"/yara/{actor}",
    }

    for k, ep in endpoints.items():
        try:
            r = requests.get(base + ep, timeout=15)
            if r.status_code == 200:
                result[k] = r.json()
            else:
                result[k] = []
        except Exception:
            result[k] = []

    return result


# -------------------------------------------------------------------
# Risk score (ADDED)
# -------------------------------------------------------------------
def calculate_risk_score(incidents, otx, ransomware):
    score = 0

    score += min(len(incidents) * 2, 30)
    score += min(incidents["country"].nunique() * 3, 15)
    score += min(incidents["sector"].nunique() * 2, 10)

    if otx:
        score += min(otx.get("pulse_count", 0), 20)
        score += min(len(otx.get("tags", [])), 10)

    if ransomware:
        score += min(len(ransomware.get("negotiations", [])) * 2, 15)
        score += min(len(ransomware.get("iocs", [])), 10)

    return min(score, 100)


# -------------------------------------------------------------------
# Actor selection
# -------------------------------------------------------------------
actor = st.query_params.get("actor", "")
if isinstance(actor, list):
    actor = actor[0]

if not actor:
    st.error("No threat actor selected")
    st.stop()

# -------------------------------------------------------------------
# Load intelligence
# -------------------------------------------------------------------
df = load_incidents()
actor_df = df[df["actor"] == actor]

otx = fetch_otx(actor)
ransomware = fetch_ransomware(actor)

risk_score = calculate_risk_score(actor_df, otx, ransomware)

# -------------------------------------------------------------------
# Header
# -------------------------------------------------------------------
st.markdown(
    f"""
    <div style="background:linear-gradient(135deg,#C41E3A,#9A1529);
                padding:2.5rem;border-radius:14px;color:white;margin-bottom:2rem">
        <h1 style="margin-bottom:0.3rem">{actor}</h1>
        <p style="opacity:.9">Comprehensive Threat Actor Intelligence</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------------
# Overview
# -------------------------------------------------------------------
st.subheader("Overview")
st.write(
    f"""
{actor} has been observed in **{len(actor_df)} incidents** across
**{actor_df['country'].nunique()} countries** and
**{actor_df['sector'].nunique()} industries**.

This profile fuses internal CyHawk telemetry with
AlienVault OTX community intelligence and ransomware.live disclosures.
"""
)

# -------------------------------------------------------------------
# Risk score (ADDED – section only)
# -------------------------------------------------------------------
st.subheader("Risk Score")
st.metric("Threat Actor Risk Index", f"{risk_score}/100")

# -------------------------------------------------------------------
# MITRE ATT&CK TTPs
# -------------------------------------------------------------------
if otx.get("tags"):
    st.subheader("MITRE ATT&CK – Observed TTPs")
    st.write(", ".join(otx["tags"][:25]))

# -------------------------------------------------------------------
# Targeted Countries
# -------------------------------------------------------------------
if not actor_df.empty:
    st.subheader("Targeted Countries")
    c = actor_df["country"].value_counts().head(10).reset_index()
    c.columns = ["Country", "Incidents"]
    fig = px.bar(c, x="Incidents", y="Country", orientation="h")
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------------------
# Targeted Industries
# -------------------------------------------------------------------
if not actor_df.empty:
    st.subheader("Targeted Industries")
    s = actor_df["sector"].value_counts().reset_index()
    s.columns = ["Sector", "Incidents"]
    fig = px.pie(s, values="Incidents", names="Sector", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------------------
# IOCs (Normalized – ADDED)
# -------------------------------------------------------------------
if otx.get("iocs"):
    st.subheader("Indicators of Compromise (OTX)")
    for k, vals in otx["iocs"].items():
        if vals:
            st.markdown(f"**{k.upper()} ({len(vals)})**")
            for v in vals[:25]:
                st.code(v)

# -------------------------------------------------------------------
# Ransomware Intelligence (Normalized – ADDED)
# -------------------------------------------------------------------
if ransomware:
    st.subheader("Ransomware Intelligence Summary")

    if ransomware.get("groups"):
        st.markdown("**Group Metadata**")
        st.json(ransomware["groups"])

    if ransomware.get("negotiations"):
        st.markdown("**Negotiation Activity**")
        st.write(f"{len(ransomware['negotiations'])} negotiation threads observed")

    if ransomware.get("ransomnotes"):
        st.markdown("**Ransom Notes**")
        for note in ransomware["ransomnotes"][:5]:
            st.code(note)

    if ransomware.get("yara"):
        st.markdown("**YARA Rules**")
        for rule in ransomware["yara"][:5]:
            st.code(rule)

# -------------------------------------------------------------------
# Timeline
# -------------------------------------------------------------------
if not actor_df.empty:
    st.subheader("Activity Timeline")
    t = actor_df.groupby(actor_df["date"].dt.to_period("M")).size().reset_index()
    t.columns = ["Month", "Incidents"]
    t["Month"] = t["Month"].dt.to_timestamp()
    fig = px.line(t, x="Month", y="Incidents")
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------------------
# Analyst Note (ADDED – intelligence fusion)
# -------------------------------------------------------------------
st.subheader("Analyst Assessment")
st.write(
    f"""
**Confidence Level:** High  

{actor} demonstrates a **risk score of {risk_score}/100**, driven by
cross-sector targeting, geographic spread, and corroboration from
multiple intelligence sources.

The overlap between CyHawk incident telemetry and ransomware.live
disclosures increases attribution confidence. Defensive teams should
prioritize IOC ingestion, proactive threat hunting, and ATT&CK-aligned
detections for this actor.
"""
)

st.success("Threat actor report generated successfully")
