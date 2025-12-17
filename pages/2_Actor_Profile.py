"""
CyHawk Africa – Threat Actor Profile
Sources:
- incidents.csv
- ransomware.live

Purpose:
Generate a comprehensive, analyst-grade threat actor report
without AlienVault OTX dependency.
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
# Data loading
# -------------------------------------------------------------------
@st.cache_data
def load_incidents():
    if not os.path.exists("data/incidents.csv"):
        return pd.DataFrame()
    df = pd.read_csv("data/incidents.csv")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df.dropna(subset=["date"])


@st.cache_data(ttl=3600)
def fetch_ransomware(actor):
    """
    Fetch comprehensive ransomware intelligence from ransomware.live
    """
    base = "https://api.ransomware.live"
    result = {}

    endpoints = {
        "groups": f"/groups/{actor}",
        "iocs": f"/iocs/{actor}",
        "negotiations": f"/negotiations/{actor}",
        "ransomnotes": f"/ransomnotes/{actor}",
        "yara": f"/yara/{actor}",
    }

    for key, endpoint in endpoints.items():
        try:
            r = requests.get(base + endpoint, timeout=15)
            if r.status_code == 200:
                result[key] = r.json()
            else:
                result[key] = []
        except Exception:
            result[key] = []

    return result


# -------------------------------------------------------------------
# Risk scoring (recalibrated – no OTX)
# -------------------------------------------------------------------
def calculate_risk_score(incidents, ransomware):
    score = 0

    # Incident volume
    score += min(len(incidents) * 2, 30)

    # Geographic spread
    score += min(incidents["country"].nunique() * 4, 20)

    # Sectoral impact
    score += min(incidents["sector"].nunique() * 3, 15)

    # Severity weighting
    if "severity" in incidents.columns:
        score += min(len(incidents[incidents["severity"] == "High"]) * 2, 15)

    # Ransomware activity indicators
    if ransomware:
        score += min(len(ransomware.get("negotiations", [])) * 3, 15)
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
ransomware = fetch_ransomware(actor)

risk_score = calculate_risk_score(actor_df, ransomware)

# -------------------------------------------------------------------
# Header
# -------------------------------------------------------------------
st.markdown(
    f"""
    <div style="background:linear-gradient(135deg,#C41E3A,#9A1529);
                padding:2.5rem;border-radius:14px;color:white;margin-bottom:2rem">
        <h1 style="margin-bottom:0.3rem">{actor}</h1>
        <p style="opacity:.9">Threat Actor Intelligence Profile</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------------
# Overview
# -------------------------------------------------------------------
st.subheader("Overview")

if not actor_df.empty:
    st.write(
        f"""
**{actor}** has been linked to **{len(actor_df)} recorded incidents**
affecting **{actor_df['country'].nunique()} countries**
and **{actor_df['sector'].nunique()} industry sectors**.

This assessment is derived from CyHawk Africa’s incident telemetry and
corroborated using ransomware infrastructure intelligence.
"""
    )
else:
    st.write(
        f"""
**{actor}** is currently tracked through external ransomware intelligence
sources, with limited confirmed incident telemetry within CyHawk datasets.
"""
    )

# -------------------------------------------------------------------
# Risk score
# -------------------------------------------------------------------
st.subheader("Risk Score")
st.metric("Threat Actor Risk Index", f"{risk_score}/100")

# -------------------------------------------------------------------
# ATT&CK-style behavioral inference
# -------------------------------------------------------------------
st.subheader("Observed Tactics & Techniques (Inferred)")

ttp_inference = []

if not actor_df.empty:
    if "ransomware" in actor.lower():
        ttp_inference.append("Data Encryption for Impact (T1486)")
        ttp_inference.append("Exfiltration Over Web Services (T1567)")
    if actor_df["sector"].nunique() > 3:
        ttp_inference.append("Targeted Vertical Operations")
    if actor_df["country"].nunique() > 5:
        ttp_inference.append("Cross-Border Targeting")

if ransomware and ransomware.get("negotiations"):
    ttp_inference.append("Double Extortion Operations")
    ttp_inference.append("Victim Negotiation Pressure")

if ttp_inference:
    st.write(", ".join(sorted(set(ttp_inference))))
else:
    st.info("Insufficient data to reliably infer ATT&CK techniques.")

# -------------------------------------------------------------------
# Targeted countries
# -------------------------------------------------------------------
if not actor_df.empty:
    st.subheader("Targeted Countries")
    c = actor_df["country"].value_counts().head(10).reset_index()
    c.columns = ["Country", "Incidents"]
    fig = px.bar(c, x="Incidents", y="Country", orientation="h")
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------------------
# Targeted industries
# -------------------------------------------------------------------
if not actor_df.empty:
    st.subheader("Targeted Industries")
    s = actor_df["sector"].value_counts().reset_index()
    s.columns = ["Sector", "Incidents"]
    fig = px.pie(s, values="Incidents", names="Sector", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------------------
# Ransomware intelligence (normalized)
# -------------------------------------------------------------------
if ransomware:
    st.subheader("Ransomware Intelligence")

    if ransomware.get("groups"):
        st.markdown("**Group Metadata**")
        st.json(ransomware["groups"])

    if ransomware.get("negotiations"):
        st.markdown("**Negotiation Activity**")
        st.write(f"{len(ransomware['negotiations'])} negotiation threads identified")

    if ransomware.get("iocs"):
        st.markdown("**Infrastructure Indicators**")
        for ioc in ransomware["iocs"][:25]:
            st.code(ioc)

    if ransomware.get("ransomnotes"):
        st.markdown("**Ransom Notes**")
        for note in ransomware["ransomnotes"][:5]:
            st.code(note)

    if ransomware.get("yara"):
        st.markdown("**YARA Detection Rules**")
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
# Analyst assessment
# -------------------------------------------------------------------
st.subheader("Analyst Assessment")

st.write(
    f"""
**Overall Risk Classification:** {'Critical' if risk_score >= 70 else 'High' if risk_score >= 40 else 'Moderate'}

{actor} demonstrates a **risk score of {risk_score}/100**, driven primarily by
incident frequency, sectoral spread, and confirmed ransomware operations.

The presence of negotiation artifacts and ransom infrastructure indicates
financial motivation and sustained operational capability.
Defensive teams should prioritize detection of encryption behaviors,
data exfiltration patterns, and ransom negotiation activity.
"""
)

st.success("Threat actor profile generated successfully")
