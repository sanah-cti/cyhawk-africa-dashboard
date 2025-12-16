import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="Threat Actors | CyHawk Africa",
    page_icon="🎯",
    layout="wide"
)

# Theme
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

CYHAWK_RED = "#C41E3A"
CYHAWK_RED_DARK = "#9A1529"

def theme_config():
    if st.session_state.theme == "dark":
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
            "danger": "#DA3633",
            "template": "plotly_dark"
        }
    return {
        "bg": "#FFFFFF",
        "bg_secondary": "#F6F8FA",
        "card": "#FFFFFF",
        "card_hover": "#F6F8FA",
        "border": "#D0D7DE",
        "text": "#1F2328",
        "text_secondary": "#636C76",
        "text_muted": "#8C959F",
        "accent": CYHAWK_RED,
        "danger": "#D1242F",
        "template": "plotly_white"
    }

C = theme_config()

# CSS
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* {{ font-family: 'Inter', sans-serif; }}
.main {{ background-color: {C['bg']}; }}
.stApp {{ background: {C['bg']}; }}

.page-header {{
    background: linear-gradient(135deg, {C['accent']} 0%, {CYHAWK_RED_DARK} 100%);
    padding: 3rem 2rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    text-align: center;
}}

.page-title {{
    color: white;
    font-size: 2.5rem;
    font-weight: 700;
    margin: 0;
}}

.page-subtitle {{
    color: rgba(255,255,255,0.9);
    font-size: 1.1rem;
    margin-top: 0.5rem;
}}

.actor-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1.5rem;
    margin-top: 2rem;
}}

.actor-card {{
    background: {C['card']};
    border: 1px solid {C['border']};
    border-radius: 12px;
    padding: 1.5rem;
    transition: all 0.3s ease;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}}

.actor-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(196, 30, 58, 0.2);
    border-color: {C['accent']};
}}

.actor-header {{
    display: flex;
    justify-content: space-between;
    align-items: start;
    margin-bottom: 1rem;
}}

.actor-name {{
    font-size: 1.25rem;
    font-weight: 700;
    color: {C['text']};
    margin: 0;
}}

.threat-level {{
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
}}

.threat-critical {{ background: {C['danger']}; color: white; }}
.threat-high {{ background: #ff6b6b; color: white; }}
.threat-medium {{ background: #ffc107; color: white; }}

.actor-meta {{
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
}}

.meta-item {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    color: {C['text_secondary']};
}}

.actor-stats {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid {C['border']};
}}

.stat {{
    text-align: center;
}}

.stat-value {{
    font-size: 1.5rem;
    font-weight: 700;
    color: {C['accent']};
}}

.stat-label {{
    font-size: 0.75rem;
    color: {C['text_muted']};
    text-transform: uppercase;
}}

.view-profile-btn {{
    width: 100%;
    padding: 0.75rem;
    background: {C['accent']};
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    margin-top: 1rem;
    cursor: pointer;
    transition: all 0.2s;
}}

.view-profile-btn:hover {{
    background: {CYHAWK_RED_DARK};
}}

@media (max-width: 768px) {{
    .actor-grid {{ grid-template-columns: 1fr; }}
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

# Header
st.markdown(f"""
<div class="page-header">
    <h1 class="page-title">Threat Actor Intelligence</h1>
    <p class="page-subtitle">Comprehensive profiles of active threat actors targeting African organizations</p>
</div>
""", unsafe_allow_html=True)

# Get actor statistics
if len(df) > 0:
    actor_stats = df.groupby('actor').agg({
        'date': 'count',
        'severity': lambda x: (x == 'High').sum(),
        'country': 'nunique',
        'sector': 'nunique'
    }).reset_index()
    actor_stats.columns = ['actor', 'total_attacks', 'high_severity', 'countries', 'sectors']
    actor_stats = actor_stats.sort_values('total_attacks', ascending=False)
    
    # Threat actor profiles database
    actor_profiles = {
        'APT28': {
            'alias': 'Fancy Bear, Sofacy',
            'origin': 'Russia',
            'active_since': '2007',
            'type': 'State-Sponsored',
            'threat_level': 'Critical',
            'description': 'Advanced persistent threat group associated with Russian military intelligence (GRU). Known for sophisticated cyber espionage campaigns.',
            'ttps': ['Spear Phishing', 'Zero-Day Exploits', 'Custom Malware', 'Credential Harvesting'],
            'targets': ['Government', 'Military', 'Critical Infrastructure', 'Media'],
            'mitre_attack': 'https://attack.mitre.org/groups/G0007/'
        },
        'Lazarus Group': {
            'alias': 'HIDDEN COBRA, Guardians of Peace',
            'origin': 'North Korea',
            'active_since': '2009',
            'type': 'State-Sponsored',
            'threat_level': 'Critical',
            'description': 'North Korean state-sponsored group known for financially motivated attacks and cyber espionage operations.',
            'ttps': ['Ransomware', 'Supply Chain Attacks', 'Cryptocurrency Theft', 'Spear Phishing'],
            'targets': ['Financial Institutions', 'Cryptocurrency Exchanges', 'Defense', 'Media'],
            'mitre_attack': 'https://attack.mitre.org/groups/G0032/'
        },
        'Anonymous Sudan': {
            'alias': 'AnonymousSudan',
            'origin': 'Sudan (Disputed)',
            'active_since': '2023',
            'type': 'Hacktivist',
            'threat_level': 'High',
            'description': 'Hacktivist group conducting DDoS attacks against Western targets. True origin and motivation remain subjects of debate.',
            'ttps': ['DDoS Attacks', 'Website Defacement', 'Social Media Campaigns'],
            'targets': ['Government Websites', 'Media Organizations', 'Corporate Sites'],
            'mitre_attack': None
        },
        'DarkSide': {
            'alias': 'DarkSide Ransomware',
            'origin': 'Eastern Europe',
            'active_since': '2020',
            'type': 'Cybercrime',
            'threat_level': 'Critical',
            'description': 'Ransomware-as-a-Service (RaaS) operator responsible for high-profile attacks on critical infrastructure.',
            'ttps': ['Ransomware', 'Double Extortion', 'Data Exfiltration', 'Network Infiltration'],
            'targets': ['Energy', 'Healthcare', 'Manufacturing', 'Retail'],
            'mitre_attack': None
        },
        'REvil': {
            'alias': 'Sodinokibi, REvil Ransomware',
            'origin': 'Russia',
            'active_since': '2019',
            'type': 'Cybercrime',
            'threat_level': 'Critical',
            'description': 'Prolific ransomware group conducting supply chain attacks and demanding multi-million dollar ransoms.',
            'ttps': ['Ransomware', 'Supply Chain Compromise', 'Zero-Day Exploitation', 'Auction-Based Extortion'],
            'targets': ['Technology', 'Legal Services', 'Healthcare', 'Government'],
            'mitre_attack': 'https://attack.mitre.org/groups/G0115/'
        }
    }
    
    # Search and filters
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_term = st.text_input("🔍 Search Threat Actors", placeholder="Search by name, origin, or type...")
    with col2:
        threat_filter = st.selectbox("Threat Level", ["All", "Critical", "High", "Medium"])
    with col3:
        sort_by = st.selectbox("Sort By", ["Total Attacks", "High Severity", "Alphabetical"])
    
    # Apply filters
    filtered_stats = actor_stats.copy()
    if search_term:
        filtered_stats = filtered_stats[filtered_stats['actor'].str.contains(search_term, case=False, na=False)]
    
    # Sort
    if sort_by == "Total Attacks":
        filtered_stats = filtered_stats.sort_values('total_attacks', ascending=False)
    elif sort_by == "High Severity":
        filtered_stats = filtered_stats.sort_values('high_severity', ascending=False)
    else:
        filtered_stats = filtered_stats.sort_values('actor')
    
    # Display actor cards
    st.markdown('<div class="actor-grid">', unsafe_allow_html=True)
    
    for _, row in filtered_stats.head(20).iterrows():
        actor_name = row['actor']
        profile = actor_profiles.get(actor_name, {
            'alias': 'Unknown',
            'origin': 'Unknown',
            'type': 'Unclassified',
            'threat_level': 'Medium',
            'active_since': 'Unknown'
        })
        
        # Determine threat level styling
        threat_level_class = {
            'Critical': 'threat-critical',
            'High': 'threat-high',
            'Medium': 'threat-medium'
        }.get(profile['threat_level'], 'threat-medium')
        
        st.markdown(f"""
        <div class="actor-card" onclick="window.location.href='?actor={actor_name}'">
            <div class="actor-header">
                <h3 class="actor-name">{actor_name}</h3>
                <span class="threat-level {threat_level_class}">{profile['threat_level']}</span>
            </div>
            <div class="actor-meta">
                <div class="meta-item">
                    <span>🌍</span>
                    <span>{profile['origin']}</span>
                </div>
                <div class="meta-item">
                    <span>🏷️</span>
                    <span>{profile['type']}</span>
                </div>
                <div class="meta-item">
                    <span>📅</span>
                    <span>Since {profile['active_since']}</span>
                </div>
            </div>
            <div class="actor-stats">
                <div class="stat">
                    <div class="stat-value">{int(row['total_attacks'])}</div>
                    <div class="stat-label">Attacks</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{int(row['countries'])}</div>
                    <div class="stat-label">Countries</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{int(row['sectors'])}</div>
                    <div class="stat-label">Sectors</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Create a button to view profile
        if st.button(f"View Profile", key=f"btn_{actor_name}", use_container_width=True):
            st.switch_page(f"pages/2_📋_Actor_Profile.py")
            st.session_state.selected_actor = actor_name
    
    st.markdown('</div>', unsafe_allow_html=True)
    
else:
    st.info("No threat actor data available. Please load incidents data.")

# Summary statistics
if len(df) > 0:
    st.markdown("---")
    st.subheader("📊 Threat Actor Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Threat Actors", len(actor_stats))
    with col2:
        critical_actors = sum(1 for actor in actor_stats['actor'] if actor_profiles.get(actor, {}).get('threat_level') == 'Critical')
        st.metric("Critical Threat Actors", critical_actors)
    with col3:
        st.metric("Total Attacks Tracked", int(actor_stats['total_attacks'].sum()))
    with col4:
        st.metric("High Severity Attacks", int(actor_stats['high_severity'].sum()))
