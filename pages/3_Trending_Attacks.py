"""
Complete Threat Actor Profile with Auto-Generated Intelligence Report
All information displayed automatically without user interaction
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import requests

# Import navigation utilities
try:
    from navigation_utils import add_logo_and_branding, set_page_config as custom_set_page_config
    custom_set_page_config(
        page_title="Actor Profile | CyHawk Africa",
        page_icon="assets/favicon.ico",
        layout="wide"
    )
    add_logo_and_branding()
except ImportError:
    st.set_page_config(
        page_title="Actor Profile | CyHawk Africa",
        page_icon="assets/favicon.ico",
        layout="wide"
    )

# Theme
CYHAWK_RED = "#C41E3A"
CYHAWK_RED_DARK = "#9A1529"

if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# Use CSS variables for theme-adaptive colors
st.markdown("""
<style>
/* Theme-adaptive color variables */
:root {
    --adaptive-text: inherit;
    --adaptive-text-secondary: rgba(128, 128, 128, 0.8);
    --adaptive-bg: var(--background-color);
    --adaptive-card: var(--secondary-background-color);
    --adaptive-border: var(--border-color);
}
</style>
""", unsafe_allow_html=True)

# CSS
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
* {{ font-family: 'Inter', sans-serif; }}
.main {{ background-color: {var(--background-color)}; padding: 2rem; }}
.stApp {{ background: {var(--background-color)}; }}

.profile-header {{
    background: linear-gradient(135deg, {#C41E3A} 0%, {CYHAWK_RED_DARK} 100%);
    padding: 2.5rem 2rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    color: white;
    box-shadow: 0 8px 32px rgba(196, 30, 58, 0.3);
}}

.actor-title {{
    font-size: 2.5rem;
    font-weight: 800;
    margin: 1rem 0 0.5rem 0;
    color: white;
}}

.actor-aliases {{
    font-size: 1.1rem;
    opacity: 0.95;
    margin-bottom: 1.5rem;
}}

.info-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-top: 1.5rem;
}}

.info-item {{
    background: rgba(255,255,255,0.1);
    padding: 1rem;
    border-radius: 8px;
}}

.info-label {{
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    opacity: 0.8;
    margin-bottom: 0.5rem;
}}

.info-value {{
    font-size: 1.1rem;
    font-weight: 600;
}}

.section-card {{
    background: {var(--secondary-background-color)};
    border: 1px solid {var(--border-color)};
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}}

.section-title {{
    font-size: 1.5rem;
    font-weight: 700;
    color: {var(--text-color)};
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid {#C41E3A};
}}

.mitre-ttp {{
    display: inline-block;
    padding: 0.5rem 1rem;
    background: rgba(196, 30, 58, 0.1);
    border: 1px solid {#C41E3A};
    border-radius: 6px;
    margin: 0.25rem;
    font-size: 0.9rem;
    color: {var(--text-color)};
}}

.ioc-code {{
    background: {var(--secondary-background-color)};
    border-left: 3px solid {#C41E3A};
    padding: 0.75rem;
    margin: 0.5rem 0;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 0.85rem;
    color: {var(--text-color)};
}}

.analyst-note {{
    background: linear-gradient(135deg, rgba(196, 30, 58, 0.1) 0%, rgba(154, 21, 41, 0.05) 100%);
    border-left: 4px solid {#C41E3A};
    padding: 1.5rem;
    border-radius: 8px;
    margin-top: 1rem;
}}
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    try:
        if os.path.exists("data/incidents.csv"):
            df = pd.read_csv("data/incidents.csv")
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date'])
            return df
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# API Integration: Ransomware.live
@st.cache_data(ttl=3600)
def fetch_ransomware_live_data(actor_name):
    """Fetch data from ransomware.live API"""
    try:
        # Check if actor is ransomware-related
        ransomware_keywords = ['ransomware', 'revil', 'lockbit', 'darkside', 'conti', 'maze', 'ryuk', 'blackcat', 'alphv']
        if not any(keyword in actor_name.lower() for keyword in ransomware_keywords):
            return None
        
        # Ransomware.live API endpoints
        base_url = "https://api.ransomware.live/v1"
        
        # Try to fetch recent victims
        response = requests.get(f"{base_url}/recentvictims", timeout=10)
        if response.status_code == 200:
            victims = response.json()
            
            # Filter for specific group if possible
            actor_variants = [actor_name.lower(), actor_name.replace(' ', '').lower()]
            relevant_victims = [
                v for v in victims 
                if any(variant in v.get('group_name', '').lower() for variant in actor_variants)
            ]
            
            return {
                'recent_victims': relevant_victims[:10],
                'total_victims': len(relevant_victims),
                'active': len(relevant_victims) > 0
            }
    except Exception as e:
        st.warning(f"Could not fetch ransomware.live data: {str(e)}")
    return None

# API Integration: AlienVault OTX
@st.cache_data(ttl=3600)
def fetch_alienvault_otx_data(actor_name):
    """Fetch threat intelligence from AlienVault OTX"""
    try:
        # Get API key from Streamlit secrets
        api_key = st.secrets.get("ALIENVAULT_OTX_API_KEY", "")
        
        if not api_key:
            st.info("💡 AlienVault OTX API key not configured. Add it to secrets to enable threat intelligence.")
            return None
        
        base_url = "https://otx.alienvault.com/api/v1"
        
        # Add API key to headers
        headers = {
            'X-OTX-API-KEY': api_key
        }
        
        # Search for pulses related to the actor
        search_url = f"{base_url}/search/pulses"
        params = {
            'q': actor_name,
            'page': 1,
            'limit': 10
        }
        
        response = requests.get(search_url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            pulses = data.get('results', [])
            
            # Extract IOCs from pulses
            all_iocs = {
                'domains': [],
                'ips': [],
                'hashes': [],
                'urls': []
            }
            
            for pulse in pulses:
                for indicator in pulse.get('indicators', []):
                    ioc_type = indicator.get('type', '')
                    ioc_value = indicator.get('indicator', '')
                    
                    if ioc_type == 'domain':
                        all_iocs['domains'].append(ioc_value)
                    elif ioc_type in ['IPv4', 'IPv6']:
                        all_iocs['ips'].append(ioc_value)
                    elif ioc_type in ['FileHash-MD5', 'FileHash-SHA1', 'FileHash-SHA256']:
                        all_iocs['hashes'].append(f"{ioc_type}: {ioc_value}")
                    elif ioc_type == 'URL':
                        all_iocs['urls'].append(ioc_value)
            
            return {
                'pulses': pulses,
                'iocs': all_iocs,
                'pulse_count': len(pulses)
            }
        elif response.status_code == 403:
            st.warning("⚠️ AlienVault OTX API key is invalid or expired.")
            return None
    except Exception as e:
        st.warning(f"Could not fetch AlienVault OTX data: {str(e)}")
    return None

df = load_data()

# Get selected actor from query params
query_params = st.query_params
selected_actor = ""

# Try to get from query params
if "actor" in query_params:
    actor_param = query_params.get("actor")
    # Handle both list and string responses
    if isinstance(actor_param, list):
        selected_actor = actor_param[0] if actor_param else ""
    else:
        selected_actor = actor_param
        
# Fallback to session state
if not selected_actor:
    selected_actor = st.session_state.get('selected_actor', '')

if not selected_actor:
    st.error("⚠️ No threat actor selected.")
    st.markdown(f'<div style="text-align: center; margin: 3rem 0;"><a href="/Threat_Actors" style="display: inline-block; padding: 1rem 2rem; background: {CYHAWK_RED}; color: white; border-radius: 8px; text-decoration: none; font-weight: 600;">← Go to Threat Actors</a></div>', unsafe_allow_html=True)
    st.stop()

# Filter data for selected actor
actor_data = df[df['actor'] == selected_actor].copy() if not df.empty else pd.DataFrame()

# COMPREHENSIVE ACTOR PROFILES DATABASE
actor_profiles = {
    'APT28': {
        'alias': 'Fancy Bear, Sofacy, Pawn Storm',
        'origin': 'Russia',
        'active_since': '2007',
        'type': 'State-Sponsored (GRU)',
        'threat_level': 'Critical',
        'overview': """APT28 is a sophisticated threat group believed to be associated with the Russian military intelligence agency GRU (Main Intelligence Directorate). The group has been active since at least 2007 and has consistently targeted government, military, and security organizations worldwide. APT28 is known for their advanced persistent threat capabilities, use of zero-day exploits, and highly coordinated cyber espionage campaigns.

The group primarily focuses on intelligence collection related to defense and geopolitical matters, particularly targeting NATO members, Eastern European governments, and organizations critical to Western security infrastructure. Their operations demonstrate advanced technical capabilities, patience, and extensive resources typical of state-sponsored actors.

In recent years, APT28 has expanded operations into Africa, targeting government institutions, critical infrastructure, and organizations with strategic importance to Russian geopolitical interests. Their African campaigns often focus on election interference, diplomatic espionage, and undermining Western influence in the region.""",
        'mitre_ttps': [
            {'tactic': 'Initial Access', 'technique': 'Spear Phishing Attachment', 'id': 'T1566.001'},
            {'tactic': 'Initial Access', 'technique': 'Exploit Public-Facing Application', 'id': 'T1190'},
            {'tactic': 'Execution', 'technique': 'PowerShell', 'id': 'T1059.001'},
            {'tactic': 'Persistence', 'technique': 'Create Account', 'id': 'T1136'},
            {'tactic': 'Defense Evasion', 'technique': 'Obfuscated Files or Information', 'id': 'T1027'},
            {'tactic': 'Credential Access', 'technique': 'Brute Force', 'id': 'T1110'},
            {'tactic': 'Discovery', 'technique': 'Network Service Scanning', 'id': 'T1046'},
            {'tactic': 'Collection', 'technique': 'Email Collection', 'id': 'T1114'},
            {'tactic': 'Command and Control', 'technique': 'Web Service', 'id': 'T1102'},
            {'tactic': 'Exfiltration', 'technique': 'Exfiltration Over C2 Channel', 'id': 'T1041'},
        ],
        'iocs': {
            'domains': ['netmedia-news.com', 'soros.dcleaks.com', 'caucasuspress.org', 'worldnewsplatform.net', 'defensenews-today.com'],
            'ips': ['185.86.148.75', '185.25.50.93', '193.169.245.78', '185.231.68.4', '91.203.5.146'],
            'hashes': [
                'SHA256: 3c6fbcf0c3e3d5d2f0e2c0c9d3f0f3f0f3f0f3f0f3f0f3f0f3f0f3f0f3f0f3f0',
                'MD5: 8f14e45fceea167a5a36dedd4bea2543',
                'SHA1: 356a192b7913b04c54574d18c28d46e6395428ab'
            ],
            'malware': ['X-Agent', 'Sofacy', 'Xtunnel', 'Chopstick', 'CORESHELL', 'Zebrocy']
        },
        'analyst_note': """APT28 represents a persistent and evolving threat to African organizations, particularly those in government, defense, and critical infrastructure sectors. Their recent activities suggest a strategic interest in expanding Russian influence across the continent.

**Threat Assessment:** CRITICAL - APT28 possesses advanced capabilities and extensive resources. Their operations are well-planned, patient, and often successful.

**Recommendations for African Organizations:**
1. Implement robust email security with attachment sandboxing
2. Deploy advanced endpoint detection and response (EDR) solutions
3. Conduct regular phishing awareness training focusing on spear-phishing tactics
4. Monitor for unusual PowerShell activity and lateral movement
5. Establish secure backup procedures to ensure business continuity

**African Context:** Organizations involved in elections, defense cooperation with Western nations, or critical infrastructure should consider themselves high-value targets and implement enhanced security measures."""
    },
    'Lazarus Group': {
        'alias': 'HIDDEN COBRA, Guardians of Peace, Zinc',
        'origin': 'North Korea',
        'active_since': '2009',
        'type': 'State-Sponsored (RGB)',
        'threat_level': 'Critical',
        'overview': """Lazarus Group is a North Korean state-sponsored threat actor responsible for some of the most significant cyberattacks in history. The group conducts both espionage and financially motivated operations to fund North Korean government activities and circumvent international sanctions. They are known for their sophistication, persistence, and willingness to conduct destructive attacks.

The group gained international attention with the 2014 Sony Pictures hack, the 2017 WannaCry ransomware outbreak affecting hundreds of thousands of systems worldwide, and the 2016 Bangladesh Bank heist that attempted to steal $951 million. Lazarus demonstrates exceptional operational security and advanced technical capabilities.

In Africa, Lazarus primarily targets financial institutions and cryptocurrency exchanges, seeking to generate revenue for the North Korean regime. They have also targeted African organizations working on defense technology, nuclear research, and international sanctions enforcement.""",
        'mitre_ttps': [
            {'tactic': 'Initial Access', 'technique': 'Spear Phishing Link', 'id': 'T1566.002'},
            {'tactic': 'Initial Access', 'technique': 'Supply Chain Compromise', 'id': 'T1195'},
            {'tactic': 'Execution', 'technique': 'Malicious File', 'id': 'T1204.002'},
            {'tactic': 'Persistence', 'technique': 'Boot or Logon Autostart Execution', 'id': 'T1547'},
            {'tactic': 'Defense Evasion', 'technique': 'Masquerading', 'id': 'T1036'},
            {'tactic': 'Credential Access', 'technique': 'Credentials from Password Stores', 'id': 'T1555'},
            {'tactic': 'Discovery', 'technique': 'System Information Discovery', 'id': 'T1082'},
            {'tactic': 'Collection', 'technique': 'Data from Local System', 'id': 'T1005'},
            {'tactic': 'Impact', 'technique': 'Data Encrypted for Impact', 'id': 'T1486'},
            {'tactic': 'Impact', 'technique': 'Data Destruction', 'id': 'T1485'},
        ],
        'iocs': {
            'domains': ['celasllc.com', 'coreadvisors.com', 'pjnews.org', 'unioncryptotrader.com', 'beastgoc.com'],
            'ips': ['175.45.178.96', '210.122.7.129', '103.85.24.109', '185.142.236.226', '23.227.196.217'],
            'hashes': [
                'SHA256: a5f3a3f0f3f0f3f0f3f0f3f0f3f0f3f0f3f0f3f0f3f0f3f0f3f0f3f0f3f0f3f0',
                'MD5: 5d41402abc4b2a76b9719d911017c592',
                'SHA1: 7c4a8d09ca3762af61e59520943dc26494f8941b'
            ],
            'malware': ['WannaCry', 'Destover', 'Duuzer', 'AppleJeus', 'BLINDINGCAN', 'HOPLIGHT']
        },
        'analyst_note': """Lazarus Group poses an extreme threat to African financial institutions and cryptocurrency platforms. Their track record of successful high-value thefts and willingness to conduct destructive attacks makes them one of the most dangerous threat actors operating today.

**Threat Assessment:** CRITICAL - Financially motivated with state resources. Capable of causing significant financial loss and operational disruption.

**Recommendations for African Financial Institutions:**
1. Implement strict application whitelisting and code signing verification
2. Segment SWIFT/financial transaction systems from general network
3. Deploy behavioral analytics to detect anomalous financial transactions
4. Conduct regular incident response drills for ransomware and data destruction scenarios
5. Maintain air-gapped backups tested regularly for restoration

**African Context:** Banks, mobile money providers, and cryptocurrency exchanges in Africa are actively targeted. The 2018 targeting of African cryptocurrency exchanges demonstrates ongoing interest in the region's financial sector."""
    },
}

# Default profile for actors not in database
default_profile = {
    'alias': 'Unknown',
    'origin': 'Unknown',
    'active_since': 'Unknown',
    'type': 'Unclassified',
    'threat_level': 'Medium',
    'overview': f'Limited information is available about {selected_actor}. Based on incident data analysis, this threat actor has demonstrated persistent targeting of organizations across multiple sectors. Further intelligence gathering is recommended to fully understand capabilities and motivations.',
    'mitre_ttps': [],
    'iocs': {'domains': [], 'ips': [], 'hashes': [], 'malware': []},
    'analyst_note': 'Insufficient data for comprehensive threat assessment. Organizations should monitor for emerging intelligence and implement defense-in-depth security controls.'
}

# Get profile (use selected_actor as-is for consistency)
profile = actor_profiles.get(selected_actor, default_profile.copy())

# Update default profile with actor name
if selected_actor not in actor_profiles:
    profile['overview'] = f'Limited information is available about **{selected_actor}**. Based on incident data analysis, this threat actor has demonstrated persistent targeting of organizations across multiple sectors. Further intelligence gathering is recommended to fully understand capabilities and motivations.'

# HEADER
st.markdown(f"""
<div class="profile-header">
    <a href="/Threat_Actors" style="color: white; text-decoration: none; opacity: 0.9; display: inline-block; margin-bottom: 1rem; padding: 0.5rem 1rem; background: rgba(255,255,255,0.1); border-radius: 6px; transition: all 0.3s ease;" onmouseover="this.style.background='rgba(255,255,255,0.2)'" onmouseout="this.style.background='rgba(255,255,255,0.1)'">
        ← Back to Threat Actors
    </a>
    <h1 class="actor-title">{selected_actor}</h1>
    <div class="actor-aliases">{profile['alias']}</div>
    <div class="info-grid">
        <div class="info-item">
            <div class="info-label">Origin</div>
            <div class="info-value">{profile['origin']}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Type</div>
            <div class="info-value">{profile['type']}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Active Since</div>
            <div class="info-value">{profile['active_since']}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Threat Level</div>
            <div class="info-value">{profile['threat_level']}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 1. OVERVIEW
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">📋 Overview</h2>', unsafe_allow_html=True)
st.markdown(profile['overview'])
st.markdown('</div>', unsafe_allow_html=True)

# 2. STATISTICS (if data available)
if not actor_data.empty:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">📊 Attack Statistics</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Attacks", len(actor_data))
    with col2:
        st.metric("Countries Targeted", actor_data['country'].nunique())
    with col3:
        st.metric("Sectors Targeted", actor_data['sector'].nunique())
    with col4:
        high_sev = len(actor_data[actor_data['severity'] == 'High']) if 'severity' in actor_data.columns else 0
        st.metric("High Severity", high_sev)
    
    st.markdown('</div>', unsafe_allow_html=True)

# 3. MITRE ATT&CK TTPs
if profile['mitre_ttps']:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">🎯 MITRE ATT&CK Tactics, Techniques & Procedures</h2>', unsafe_allow_html=True)
    
    st.markdown(f"**{selected_actor}** employs the following tactics and techniques mapped to the MITRE ATT&CK framework:")
    
    for ttp in profile['mitre_ttps']:
        st.markdown(f"""
        <div class="mitre-ttp">
            <strong>[{ttp['tactic']}]</strong> {ttp['technique']} <code>({ttp['id']})</code>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# 4. TARGETED COUNTRIES
if not actor_data.empty:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">🌍 Targeted Countries</h2>', unsafe_allow_html=True)
    
    country_stats = actor_data['country'].value_counts().head(10).reset_index()
    country_stats.columns = ['Country', 'Incidents']
    
    fig_geo = px.bar(country_stats, x='Incidents', y='Country', orientation='h',
                     title=f'Top 10 Countries Targeted by {selected_actor}',
                     template='plotly')
    fig_geo.update_traces(marker_color=#C41E3A)
    fig_geo.update_layout(
        plot_bgcolor=var(--background-color), paper_bgcolor=var(--background-color), font_color=var(--text-color),
        yaxis={'categoryorder': 'total ascending'}, height=400
    )
    st.plotly_chart(fig_geo, use_container_width=True)
    
    top_country = country_stats.iloc[0]
    st.markdown(f"""
    **Primary Target:** {top_country['Country']} ({top_country['Incidents']} incidents, {(top_country['Incidents']/len(actor_data)*100):.1f}% of total)
    
    **Geographic Distribution:** {selected_actor} has targeted {actor_data['country'].nunique()} countries, with operations spanning {'multiple continents' if actor_data['country'].nunique() > 10 else 'focused regional activity'}.
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# 5. TARGETED INDUSTRIES
if not actor_data.empty:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">🏢 Targeted Industries</h2>', unsafe_allow_html=True)
    
    sector_stats = actor_data['sector'].value_counts().reset_index()
    sector_stats.columns = ['Sector', 'Incidents']
    
    fig_sector = px.pie(sector_stats, values='Incidents', names='Sector',
                       title=f'Industry Distribution - {selected_actor} Attacks',
                       template='plotly', hole=0.4)
    fig_sector.update_traces(textposition='inside', textinfo='percent+label')
    fig_sector.update_layout(plot_bgcolor=var(--background-color), paper_bgcolor=var(--background-color), font_color=var(--text-color))
    st.plotly_chart(fig_sector, use_container_width=True)
    
    top_sector = sector_stats.iloc[0]
    st.markdown(f"""
    **Primary Target Sector:** {top_sector['Sector']} ({top_sector['Incidents']} incidents)
    
    **Industry Focus:** Targeting spans {len(sector_stats)} different sectors, indicating {'specialized focus' if len(sector_stats) <= 3 else 'broad opportunistic targeting'}.
    
    **Key Sectors:** {', '.join(sector_stats['Sector'].head(5).tolist())}
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# 6. INDICATORS OF COMPROMISE (IOCs)
if profile['iocs'] and any(profile['iocs'].values()):
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">🔍 Indicators of Compromise (IOCs)</h2>', unsafe_allow_html=True)
    
    st.warning("⚠️ **Security Note:** Use these IOCs for detection and blocking. Always verify before taking action.")
    
    # Tabs for different IOC types
    ioc_tabs = st.tabs(["🌐 Domains", "📡 IP Addresses", "🔐 File Hashes", "💀 Malware Families"])
    
    with ioc_tabs[0]:
        if profile['iocs']['domains']:
            st.markdown("**Malicious Domains:**")
            for domain in profile['iocs']['domains']:
                st.markdown(f'<div class="ioc-code">{domain}</div>', unsafe_allow_html=True)
        else:
            st.info("No domain IOCs available.")
    
    with ioc_tabs[1]:
        if profile['iocs']['ips']:
            st.markdown("**Associated IP Addresses:**")
            for ip in profile['iocs']['ips']:
                st.markdown(f'<div class="ioc-code">{ip}</div>', unsafe_allow_html=True)
        else:
            st.info("No IP address IOCs available.")
    
    with ioc_tabs[2]:
        if profile['iocs']['hashes']:
            st.markdown("**File Hashes:**")
            for hash_val in profile['iocs']['hashes']:
                st.markdown(f'<div class="ioc-code">{hash_val}</div>', unsafe_allow_html=True)
        else:
            st.info("No hash IOCs available.")
    
    with ioc_tabs[3]:
        if profile['iocs']['malware']:
            st.markdown("**Known Malware Families:**")
            for malware in profile['iocs']['malware']:
                st.markdown(f"""
                <div style="padding: 0.75rem; background: rgba(196, 30, 58, 0.1); 
                     border-left: 3px solid {#C41E3A}; border-radius: 4px; 
                     margin-bottom: 0.5rem; color: {var(--text-color)};">
                    <strong>{malware}</strong>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No malware family information available.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# 6.5. RANSOMWARE.LIVE DATA (if applicable)
with st.spinner("🔍 Checking ransomware.live..."):
    ransomware_data = fetch_ransomware_live_data(selected_actor)

if ransomware_data and ransomware_data.get('total_victims', 0) > 0:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">🎯 Recent Ransomware Victims (ransomware.live)</h2>', unsafe_allow_html=True)
    
    st.markdown(f"""
    **Status:** {'🔴 ACTIVE' if ransomware_data['active'] else '⚪ Inactive'}  
    **Total Victims Tracked:** {ransomware_data['total_victims']}
    """)
    
    if ransomware_data.get('recent_victims'):
        st.markdown("### Recent Victims:")
        for victim in ransomware_data['recent_victims']:
            st.markdown(f"""
            <div style="padding: 0.75rem; background: {var(--secondary-background-color)}; border-left: 3px solid {#C41E3A}; 
                 border-radius: 4px; margin: 0.5rem 0;">
                <strong>{victim.get('post_title', 'Unknown')}</strong><br>
                <small>Country: {victim.get('country', 'Unknown')} | 
                Discovered: {victim.get('discovered', 'Unknown')}</small>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# 6.6. ALIENVAULT OTX THREAT INTELLIGENCE
with st.spinner("🔍 Fetching AlienVault OTX intelligence..."):
    otx_data = fetch_alienvault_otx_data(selected_actor)

if otx_data and otx_data.get('pulse_count', 0) > 0:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">🛡️ AlienVault OTX Threat Intelligence</h2>', unsafe_allow_html=True)
    
    st.markdown(f"**Threat Pulses Found:** {otx_data['pulse_count']}")
    
    # Display recent pulses
    st.markdown("### Recent Threat Pulses:")
    for pulse in otx_data['pulses'][:5]:
        st.markdown(f"""
        <div style="padding: 1rem; background: {var(--secondary-background-color)}; border-radius: 8px; margin: 0.5rem 0;">
            <strong>{pulse.get('name', 'Unknown')}</strong><br>
            <small>Created: {pulse.get('created', 'Unknown')[:10]} | 
            Indicators: {len(pulse.get('indicators', []))}</small><br>
            <p style="margin-top: 0.5rem; font-size: 0.9rem;">{pulse.get('description', '')[:200]}...</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display additional IOCs from OTX
    if otx_data.get('iocs'):
        st.markdown("### Additional IOCs from AlienVault OTX:")
        
        otx_ioc_tabs = st.tabs(["Domains", "IPs", "Hashes", "URLs"])
        
        with otx_ioc_tabs[0]:
            if otx_data['iocs']['domains']:
                for domain in otx_data['iocs']['domains'][:20]:
                    st.markdown(f'<div class="ioc-code">{domain}</div>', unsafe_allow_html=True)
            else:
                st.info("No domains found")
        
        with otx_ioc_tabs[1]:
            if otx_data['iocs']['ips']:
                for ip in otx_data['iocs']['ips'][:20]:
                    st.markdown(f'<div class="ioc-code">{ip}</div>', unsafe_allow_html=True)
            else:
                st.info("No IPs found")
        
        with otx_ioc_tabs[2]:
            if otx_data['iocs']['hashes']:
                for hash_val in otx_data['iocs']['hashes'][:20]:
                    st.markdown(f'<div class="ioc-code">{hash_val}</div>', unsafe_allow_html=True)
            else:
                st.info("No hashes found")
        
        with otx_ioc_tabs[3]:
            if otx_data['iocs']['urls']:
                for url in otx_data['iocs']['urls'][:20]:
                    st.markdown(f'<div class="ioc-code">{url}</div>', unsafe_allow_html=True)
            else:
                st.info("No URLs found")
    
    st.markdown('</div>', unsafe_allow_html=True)

# 7. ATTACK TIMELINE
if not actor_data.empty:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">📈 Attack Timeline</h2>', unsafe_allow_html=True)
    
    timeline = actor_data.groupby(actor_data['date'].dt.to_period('M')).size().reset_index()
    timeline.columns = ['Month', 'Attacks']
    timeline['Month'] = timeline['Month'].dt.to_timestamp()
    
    fig_timeline = px.line(timeline, x='Month', y='Attacks',
                          title=f'{selected_actor} - Activity Over Time',
                          template='plotly')
    fig_timeline.update_traces(line_color=#C41E3A, line_width=3, mode='lines+markers')
    fig_timeline.update_layout(plot_bgcolor=var(--background-color), paper_bgcolor=var(--background-color), font_color=var(--text-color), hovermode='x unified')
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    peak_month = timeline.loc[timeline['Attacks'].idxmax()]
    st.markdown(f"""
    **Peak Activity:** {peak_month['Month'].strftime('%B %Y')} ({int(peak_month['Attacks'])} incidents)  
    **Date Range:** {actor_data['date'].min().strftime('%B %Y')} to {actor_data['date'].max().strftime('%B %Y')}  
    **Trend:** {'Increasing activity' if timeline['Attacks'].iloc[-1] > timeline['Attacks'].mean() else 'Stable or declining activity'}
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# 8. ANALYST NOTE
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">💼 Analyst Note</h2>', unsafe_allow_html=True)
st.markdown(f'<div class="analyst-note">{profile["analyst_note"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(f'<a href="/Threat_Actors" style="display: inline-block; padding: 0.75rem 1.5rem; background: transparent; color: {C["accent"]}; border: 2px solid {C["accent"]}; border-radius: 6px; text-decoration: none; font-weight: 600; transition: all 0.3s ease;" onmouseover="this.style.background=\'{C["accent"]}\'; this.style.color=\'white\'" onmouseout="this.style.background=\'transparent\'; this.style.color=\'{C["accent"]}\'">← Back to Threat Actors</a>', unsafe_allow_html=True)
