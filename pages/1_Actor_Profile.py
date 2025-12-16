import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="Actor Profile | CyHawk Africa",
    page_icon="📋",
    layout="wide"
)

# Get selected actor from URL or session state
query_params = st.query_params
selected_actor = query_params.get("actor", [""])[0] if "actor" in query_params else st.session_state.get('selected_actor', '')

if not selected_actor:
    st.warning("⚠️ No threat actor selected. Please go back to Threat Actors page.")
    if st.button("← Back to Threat Actors"):
        st.switch_page("pages/1_🎯_Threat_Actors.py")
    st.stop()

# Theme
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

CYHAWK_RED = "#C41E3A"

def theme_config():
    if st.session_state.theme == "dark":
        return {
            "bg": "#0D1117",
            "card": "#1C2128",
            "border": "#30363D",
            "text": "#E6EDF3",
            "text_secondary": "#8B949E",
            "text_muted": "#6E7681",
            "accent": CYHAWK_RED,
            "danger": "#DA3633",
            "warning": "#ffc107",
            "success": "#238636",
            "template": "plotly_dark"
        }
    return {
        "bg": "#FFFFFF",
        "card": "#FFFFFF",
        "border": "#D0D7DE",
        "text": "#1F2328",
        "text_secondary": "#636C76",
        "text_muted": "#8C959F",
        "accent": CYHAWK_RED,
        "danger": "#D1242F",
        "warning": "#f59e0b",
        "success": "#1A7F37",
        "template": "plotly_white"
    }

C = theme_config()

# CSS
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* {{ font-family: 'Inter', sans-serif; }}
.main {{ background-color: {C['bg']}; }}

.profile-header {{
    background: linear-gradient(135deg, {C['accent']} 0%, #9A1529 100%);
    padding: 2rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    color: white;
}}

.actor-title {{
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}}

.actor-aliases {{
    font-size: 1.1rem;
    opacity: 0.9;
    margin-bottom: 1rem;
}}

.info-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}}

.info-item {{
    background: rgba(255,255,255,0.1);
    padding: 1rem;
    border-radius: 8px;
}}

.info-label {{
    font-size: 0.75rem;
    text-transform: uppercase;
    opacity: 0.8;
    margin-bottom: 0.25rem;
}}

.info-value {{
    font-size: 1.25rem;
    font-weight: 600;
}}

.section-card {{
    background: {C['card']};
    border: 1px solid {C['border']};
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}}

.section-title {{
    font-size: 1.25rem;
    font-weight: 700;
    color: {C['text']};
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid {C['accent']};
}}

.ttp-badge {{
    display: inline-block;
    padding: 0.5rem 1rem;
    background: {C['accent']};
    color: white;
    border-radius: 6px;
    margin: 0.25rem;
    font-size: 0.875rem;
    font-weight: 500;
}}

.target-item {{
    padding: 0.75rem;
    background: rgba(196, 30, 58, 0.1);
    border-left: 3px solid {C['accent']};
    border-radius: 4px;
    margin-bottom: 0.5rem;
}}

.mitre-link {{
    display: inline-flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem 1.5rem;
    background: linear-gradient(135deg, #ff9500 0%, #ff6b00 100%);
    color: white;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 600;
    font-size: 1rem;
    margin: 1.5rem 0;
    transition: all 0.3s;
    box-shadow: 0 4px 12px rgba(255, 149, 0, 0.3);
}}

.mitre-link:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(255, 149, 0, 0.4);
}}

.mitre-icon {{
    font-size: 1.5rem;
}}
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    try:
        csv_path = 'data/incidents.csv'
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date'])
            
            categorical_columns = ['actor', 'country', 'threat_type', 'sector', 'severity', 'source']
            for col in categorical_columns:
                if col in df.columns:
                    df[col] = df[col].fillna('Unknown').astype(str)
            
            return df
        else:
            return pd.DataFrame()
    except:
        return pd.DataFrame()

df = load_data()

# Actor profiles database
actor_profiles = {
    'APT28': {
        'alias': 'Fancy Bear, Sofacy, Pawn Storm',
        'origin': 'Russia',
        'active_since': '2007',
        'type': 'State-Sponsored (GRU)',
        'threat_level': 'Critical',
        'mitre_attack': 'https://attack.mitre.org/groups/G0007/',
        'description': 'APT28 is a sophisticated threat group believed to be associated with the Russian military intelligence agency GRU. The group has been active since at least 2007 and has targeted governments, militaries, and security organizations worldwide. They are known for their advanced persistent threat capabilities and use of zero-day exploits.',
        'ttps': ['Spear Phishing', 'Zero-Day Exploits', 'Custom Malware (X-Agent, Sofacy)', 'Credential Harvesting', 'Watering Hole Attacks'],
        'targets': ['Government', 'Military', 'Critical Infrastructure', 'Media', 'Political Organizations'],
        'notable_attacks': [
            'DNC Email Breach (2016)',
            'German Parliament Attack (2015)',
            'Ukrainian Power Grid (2015)',
            'Olympic Destroyer Campaign (2018)'
        ]
    },
    'Lazarus Group': {
        'alias': 'HIDDEN COBRA, Guardians of Peace, Zinc',
        'origin': 'North Korea',
        'active_since': '2009',
        'type': 'State-Sponsored (RGB)',
        'threat_level': 'Critical',
        'mitre_attack': 'https://attack.mitre.org/groups/G0032/',
        'description': 'Lazarus Group is a North Korean state-sponsored threat actor responsible for some of the most significant cyberattacks in history. The group conducts both espionage and financially motivated operations to fund North Korean government activities.',
        'ttps': ['Ransomware (WannaCry)', 'Supply Chain Attacks', 'Cryptocurrency Theft', 'Spear Phishing', 'Custom Backdoors'],
        'targets': ['Financial Institutions', 'Cryptocurrency Exchanges', 'Defense Industry', 'Media Companies', 'Government'],
        'notable_attacks': [
            'Sony Pictures Hack (2014)',
            'WannaCry Ransomware (2017)',
            'Bangladesh Bank Heist (2016) - $81M stolen',
            'Operation AppleJeus (Cryptocurrency theft)'
        ]
    },
    'Anonymous Sudan': {
        'alias': 'AnonymousSudan',
        'origin': 'Sudan (Attribution Disputed)',
        'active_since': '2023',
        'type': 'Hacktivist (Possibly Pro-Russian)',
        'threat_level': 'High',
        'mitre_attack': None,
        'description': 'Anonymous Sudan emerged in early 2023 claiming to be a hacktivist group from Sudan. However, security researchers have found evidence suggesting possible ties to Russian interests. The group primarily conducts DDoS attacks against Western targets.',
        'ttps': ['Distributed Denial of Service (DDoS)', 'Website Defacement', 'Social Media Campaigns', 'Telegram-based Operations'],
        'targets': ['Government Websites', 'Media Organizations', 'Corporate Websites', 'Critical Infrastructure Portals'],
        'notable_attacks': [
            'Microsoft Azure DDoS (June 2023)',
            'Multiple European Government Sites',
            'African Union Website',
            'Various Western Media Outlets'
        ]
    },
    'DarkSide': {
        'alias': 'DarkSide Ransomware',
        'origin': 'Eastern Europe (Russia/CIS)',
        'active_since': '2020',
        'type': 'Cybercrime (Ransomware-as-a-Service)',
        'threat_level': 'Critical',
        'mitre_attack': None,
        'description': 'DarkSide is a ransomware-as-a-service (RaaS) operation that emerged in 2020. The group operates a professional criminal enterprise, avoiding targets in CIS countries and claiming to donate portions of ransom payments to charity. They employ double extortion tactics.',
        'ttps': ['Ransomware Deployment', 'Double Extortion', 'Data Exfiltration', 'Network Reconnaissance', 'Lateral Movement'],
        'targets': ['Energy Sector', 'Healthcare', 'Manufacturing', 'Retail', 'Legal Services'],
        'notable_attacks': [
            'Colonial Pipeline (May 2021) - $4.4M ransom',
            'Toshiba European Operations (2021)',
            'CompuCom (March 2021)',
            'Multiple Fortune 500 Companies'
        ]
    },
    'REvil': {
        'alias': 'Sodinokibi, REvil Ransomware',
        'origin': 'Russia',
        'active_since': '2019',
        'type': 'Cybercrime (Ransomware-as-a-Service)',
        'threat_level': 'Critical',
        'mitre_attack': 'https://attack.mitre.org/groups/G0115/',
        'description': 'REvil is one of the most prolific ransomware groups, responsible for numerous high-profile attacks. They pioneered auction-based extortion and supply chain attacks. The group went offline in 2021 but has shown signs of attempting to resurface.',
        'ttps': ['Ransomware Deployment', 'Supply Chain Compromise', 'Zero-Day Exploitation', 'Auction-Based Extortion', 'Affiliate Program'],
        'targets': ['Technology Companies', 'Legal Services', 'Healthcare', 'Government', 'Managed Service Providers'],
        'notable_attacks': [
            'Kaseya Supply Chain Attack (July 2021) - 1,500+ companies',
            'JBS Foods (June 2021) - $11M ransom',
            'Acer (March 2021) - $50M demand',
            'Apple Supplier Quanta (April 2021)'
        ]
    }
}

# Get profile or use default
profile = actor_profiles.get(selected_actor, {
    'alias': 'Unknown',
    'origin': 'Unknown',
    'active_since': 'Unknown',
    'type': 'Unclassified',
    'threat_level': 'Medium',
    'mitre_attack': None,
    'description': f'No detailed profile available for {selected_actor}.',
    'ttps': ['Information Not Available'],
    'targets': ['Various'],
    'notable_attacks': ['Information Not Available']
})

# Filter data for this actor
actor_df = df[df['actor'] == selected_actor]

# Header
st.markdown(f"""
<div class="profile-header">
    <a href="?page=actors" style="color: white; text-decoration: none; opacity: 0.8;">← Back to Threat Actors</a>
    <h1 class="actor-title">{selected_actor}</h1>
    <div class="actor-aliases">{profile['alias']}</div>
    <div class="info-grid">
        <div class="info-item">
            <div class="info-label">Origin</div>
            <div class="info-value">🌍 {profile['origin']}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Type</div>
            <div class="info-value">🏷️ {profile['type']}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Active Since</div>
            <div class="info-value">📅 {profile['active_since']}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Threat Level</div>
            <div class="info-value">⚠️ {profile['threat_level']}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Overview
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">📖 Overview</h2>', unsafe_allow_html=True)
st.markdown(f"<p style='color: {C['text']}; line-height: 1.6;'>{profile['description']}</p>", unsafe_allow_html=True)

# MITRE ATT&CK Link if available
if profile.get('mitre_attack'):
    st.markdown(f"""
    <a href="{profile['mitre_attack']}" target="_blank" class="mitre-link">
        <span class="mitre-icon">🔗</span>
        <div>
            <div style="font-weight: 700;">View MITRE ATT&CK Profile</div>
            <div style="font-size: 0.875rem; opacity: 0.9;">Comprehensive TTPs and techniques mapping</div>
        </div>
    </a>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Tactics, Techniques & Procedures
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">🛠️ Tactics, Techniques & Procedures (TTPs)</h2>', unsafe_allow_html=True)
    for ttp in profile['ttps']:
        st.markdown(f'<span class="ttp-badge">{ttp}</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">🎯 Primary Targets</h2>', unsafe_allow_html=True)
    for target in profile['targets']:
        st.markdown(f'<div class="target-item">{target}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Notable Attacks
if 'notable_attacks' in profile:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">💥 Notable Attacks</h2>', unsafe_allow_html=True)
    for attack in profile['notable_attacks']:
        st.markdown(f"- **{attack}**")
    st.markdown('</div>', unsafe_allow_html=True)

# Activity Statistics (if data available)
if len(actor_df) > 0:
    st.markdown("---")
    st.subheader("📊 Activity Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Attacks", len(actor_df))
    with col2:
        high_sev = len(actor_df[actor_df['severity'] == 'High'])
        st.metric("High Severity", high_sev)
    with col3:
        st.metric("Countries Targeted", actor_df['country'].nunique())
    with col4:
        st.metric("Sectors Affected", actor_df['sector'].nunique())
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("**Attack Timeline**")
        timeline = actor_df.groupby(actor_df['date'].dt.date).size().reset_index()
        timeline.columns = ['Date', 'Count']
        fig = px.line(timeline, x='Date', y='Count', template=C['template'])
        fig.update_traces(line_color=C['accent'])
        fig.update_layout(height=250, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("**Top Targeted Countries**")
        countries = actor_df['country'].value_counts().head(5).reset_index()
        countries.columns = ['Country', 'Count']
        fig = px.bar(countries, x='Count', y='Country', orientation='h', template=C['template'])
        fig.update_traces(marker_color=C['accent'])
        fig.update_layout(height=250, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

# Back button
if st.button("← Back to Threat Actors", use_container_width=False):
    st.switch_page("pages/1_🎯_Threat_Actors.py")
