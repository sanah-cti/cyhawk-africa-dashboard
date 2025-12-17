import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# ======================
# CyHawk Brand Constants
# ======================
CYHAWK_RED = "#C41E3A"
CYHAWK_RED_DARK = "#9A1529"

# ======================
# Page Configuration
# ======================
st.set_page_config(
    page_title="Actor Profile | CyHawk Africa",
    page_icon="📋",
    layout="wide"
)

# ======================
# Theme
# ======================
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def theme_config():
    return {
        "bg": "#0D1117",
        "card": "#1C2128",
        "border": "#30363D",
        "text": "#E6EDF3",
        "text_secondary": "#8B949E",
        "accent": CYHAWK_RED,
        "template": "plotly_dark"
    }

C = theme_config()

# ======================
# Get Selected Actor
# ======================
query_params = st.query_params
selected_actor = (
    query_params.get("actor", [""])[0]
    if "actor" in query_params
    else st.session_state.get("selected_actor", "")
)

if not selected_actor:
    st.warning("No threat actor selected. Please select an actor from the Threat Actors page.")
    st.markdown(
        f"""
        <div style="text-align:center; margin:3rem 0;">
            <a href="Threat_Actors"
               style="padding:1rem 2rem;
                      background:{CYHAWK_RED};
                      color:white;
                      border-radius:8px;
                      text-decoration:none;
                      font-weight:600;">
               ← Go to Threat Actors
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.stop()

# ======================
# Actor Profiles Database (Versioned)
# ======================
actor_profiles = {
    "APT28": {
        "alias": "Fancy Bear, Sofacy, Pawn Storm",
        "origin": "Russia",
        "type": "State-Sponsored (GRU)",
        "active_since": "2007",
        "threat_level": "Critical",

        # 🔹 Versioning
        "profile_version": "v1.3",
        "last_updated": "2025-01-08",
        "confidence_level": "High",

        "mitre_attack": "https://attack.mitre.org/groups/G0007/",
        "description": (
            "APT28 is a Russian state-sponsored threat actor linked to the GRU. "
            "It conducts cyber espionage, influence operations, and targeted intrusions "
            "against government, military, and political entities."
        ),
        "ttps": [
            "Spear Phishing",
            "Credential Harvesting",
            "Zero-Day Exploits",
            "Custom Malware (X-Agent, Sofacy)",
            "Lateral Movement"
        ],
        "targets": [
            "Government",
            "Military",
            "Critical Infrastructure",
            "Political Organizations",
            "Media"
        ],
        "notable_attacks": [
            "DNC Email Breach (2016)",
            "German Bundestag Attack (2015)",
            "Olympic Destroyer Campaign (2018)"
        ]
    },

    "Lazarus Group": {
        "alias": "Hidden Cobra, Zinc",
        "origin": "North Korea",
        "type": "State-Sponsored (RGB)",
        "active_since": "2009",
        "threat_level": "Critical",

        "profile_version": "v2.1",
        "last_updated": "2025-01-10",
        "confidence_level": "High",

        "mitre_attack": "https://attack.mitre.org/groups/G0032/",
        "description": (
            "Lazarus Group is a North Korean state-sponsored actor responsible for "
            "cyber espionage, destructive attacks, and large-scale financial theft."
        ),
        "ttps": [
            "Ransomware (WannaCry)",
            "Supply Chain Attacks",
            "Cryptocurrency Theft",
            "Custom Backdoors"
        ],
        "targets": [
            "Financial Institutions",
            "Cryptocurrency Exchanges",
            "Defense Industry",
            "Government"
        ],
        "notable_attacks": [
            "Sony Pictures Hack (2014)",
            "WannaCry Ransomware (2017)",
            "Bangladesh Bank Heist (2016)"
        ]
    }
}

# ======================
# Load Profile
# ======================
profile = actor_profiles.get(selected_actor)

if not profile:
    st.error(f"No detailed profile available for {selected_actor}.")
    st.stop()

# ======================
# Header
# ======================
st.markdown(
    f"""
    <div style="
        background:linear-gradient(135deg, {CYHAWK_RED}, {CYHAWK_RED_DARK});
        padding:2rem;
        border-radius:12px;
        color:white;
        margin-bottom:2rem;
    ">
        <a href="Threat_Actors"
           style="color:white; text-decoration:none; opacity:0.85;">
           ← Back to Threat Actors
        </a>

        <h1 style="margin-top:1rem;">{selected_actor}</h1>
        <p style="opacity:0.9;">{profile['alias']}</p>

        <div style="display:flex; gap:1.5rem; flex-wrap:wrap; margin-top:1rem;">
            <div><strong>Origin:</strong> {profile['origin']}</div>
            <div><strong>Type:</strong> {profile['type']}</div>
            <div><strong>Threat Level:</strong> {profile['threat_level']}</div>
            <div><strong>Active Since:</strong> {profile['active_since']}</div>
        </div>

        <!-- 🔹 Version Badge -->
        <div style="
            margin-top:1.5rem;
            display:inline-block;
            padding:0.4rem 0.75rem;
            background:rgba(255,255,255,0.15);
            border-radius:6px;
            font-size:0.85rem;
        ">
            Profile {profile['profile_version']} · Updated {profile['last_updated']} · Confidence: {profile['confidence_level']}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ======================
# Overview
# ======================
st.markdown(
    f"""
    <div style="background:{C['card']};
                border:1px solid {C['border']};
                border-radius:12px;
                padding:1.5rem;
                margin-bottom:1.5rem;">
        <h2>Overview</h2>
        <p style="line-height:1.6;">{profile['description']}</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ======================
# TTPs & Targets
# ======================
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"""
        <div style="background:{C['card']};
                    border:1px solid {C['border']};
                    border-radius:12px;
                    padding:1.5rem;">
            <h3>Tactics, Techniques & Procedures</h3>
        """,
        unsafe_allow_html=True
    )
    for ttp in profile["ttps"]:
        st.markdown(
            f"""
            <span style="
                display:inline-block;
                margin:0.25rem;
                padding:0.4rem 0.75rem;
                background:{CYHAWK_RED};
                border-radius:6px;
                color:white;
                font-size:0.85rem;">
                {ttp}
            </span>
            """,
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown(
        f"""
        <div style="background:{C['card']};
                    border:1px solid {C['border']};
                    border-radius:12px;
                    padding:1.5rem;">
            <h3>Primary Targets</h3>
        """,
        unsafe_allow_html=True
    )
    for target in profile["targets"]:
        st.markdown(f"- **{target}**")
    st.markdown("</div>", unsafe_allow_html=True)

# ======================
# MITRE ATT&CK
# ======================
if profile.get("mitre_attack"):
    st.markdown(
        f"""
        <a href="{profile['mitre_attack']}" target="_blank"
           style="
               display:inline-block;
               margin-top:2rem;
               padding:1rem 1.5rem;
               background:#ff9500;
               color:white;
               border-radius:8px;
               text-decoration:none;
               font-weight:600;">
            View MITRE ATT&CK Mapping
        </a>
        """,
        unsafe_allow_html=True
    )
