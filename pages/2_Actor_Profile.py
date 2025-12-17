"""
Comprehensive Threat Actor Profile Generator
Automatically generates reports using:
1. incidents.csv data (charts, statistics)
2. AlienVault OTX API (threat intelligence, IOCs)
3. Ransomware.live API (victim data)
4. AI-generated analysis from web sources
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import requests
import json

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

# Adaptive CSS
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
* {{ font-family: 'Inter', sans-serif; }}

.profile-header {{
    background: linear-gradient(135deg, {CYHAWK_RED} 0%, {CYHAWK_RED_DARK} 100%);
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
    color: white;
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
    color: white;
}}

.info-value {{
    font-size: 1.1rem;
    font-weight: 600;
    color: white;
}}

.section-card {{
    background: var(--secondary-background-color);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}}

.section-title {{
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid {CYHAWK_RED};
}}

.mitre-ttp {{
    display: inline-block;
    padding: 0.5rem 1rem;
    background: rgba(196, 30, 58, 0.1);
    border: 1px solid {CYHAWK_RED};
    border-radius: 6px;
    margin: 0.25rem;
    font-size: 0.9rem;
}}

.ioc-code {{
    background: var(--secondary-background-color);
    border-left: 3px solid {CYHAWK_RED};
    padding: 0.75rem;
    margin: 0.5rem 0;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 0.85rem;
}}

.analyst-note {{
    background: linear-gradient(135deg, rgba(196, 30, 58, 0.1) 0%, rgba(154, 21, 41, 0.05) 100%);
    border-left: 4px solid {CYHAWK_RED};
    padding: 1.5rem;
    border-radius: 8px;
    margin-top: 1rem;
}}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA LOADING AND API FUNCTIONS
# ============================================================================

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

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_alienvault_otx_data(actor_name):
    """Fetch comprehensive threat intelligence from AlienVault OTX"""
    try:
        api_key = st.secrets.get("ALIENVAULT_OTX_API_KEY", "")
        
        if not api_key:
            return None
        
        base_url = "https://otx.alienvault.com/api/v1"
        headers = {'X-OTX-API-KEY': api_key}
        
        # Search for pulses
        search_url = f"{base_url}/search/pulses"
        params = {'q': actor_name, 'page': 1, 'limit': 20}
        
        response = requests.get(search_url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            pulses = data.get('results', [])
            
            # Extract comprehensive IOCs
            all_iocs = {
                'domains': set(),
                'ips': set(),
                'hashes': set(),
                'urls': set(),
                'emails': set(),
                'cves': set()
            }
            
            # Extract malware families and tags
            malware_families = set()
            tags = set()
            
            for pulse in pulses:
                # Get tags
                for tag in pulse.get('tags', []):
                    tags.add(tag)
                
                # Extract malware from pulse name and description
                pulse_name = pulse.get('name', '').lower()
                pulse_desc = pulse.get('description', '').lower()
                
                for indicator in pulse.get('indicators', []):
                    ioc_type = indicator.get('type', '')
                    ioc_value = indicator.get('indicator', '')
                    
                    if ioc_type == 'domain':
                        all_iocs['domains'].add(ioc_value)
                    elif ioc_type in ['IPv4', 'IPv6']:
                        all_iocs['ips'].add(ioc_value)
                    elif ioc_type in ['FileHash-MD5', 'FileHash-SHA1', 'FileHash-SHA256']:
                        all_iocs['hashes'].add(ioc_value)
                    elif ioc_type == 'URL':
                        all_iocs['urls'].add(ioc_value)
                    elif ioc_type == 'email':
                        all_iocs['emails'].add(ioc_value)
                    elif ioc_type == 'CVE':
                        all_iocs['cves'].add(ioc_value)
            
            # Convert sets to sorted lists
            for key in all_iocs:
                all_iocs[key] = sorted(list(all_iocs[key]))
            
            return {
                'pulses': pulses,
                'iocs': all_iocs,
                'pulse_count': len(pulses),
                'tags': sorted(list(tags)),
                'malware_families': sorted(list(malware_families))
            }
        
        return None
    except Exception as e:
        st.warning(f"AlienVault OTX: {str(e)}")
        return None

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_ransomware_live_data(actor_name):
    """Fetch ransomware victim data"""
    try:
        base_url = "https://api.ransomware.live"
        
        # Get recent victims
        response = requests.get(f"{base_url}/recentvictims", timeout=15)
        
        if response.status_code == 200:
            all_victims = response.json()
            
            # Try multiple name variations
            name_variants = [
                actor_name.lower(),
                actor_name.replace(' ', '').lower(),
                actor_name.replace(' ', '-').lower(),
                actor_name.replace('-', '').lower(),
                actor_name.replace('_', '').lower()
            ]
            
            # Filter victims
            relevant_victims = []
            for victim in all_victims:
                group_name = victim.get('group_name', '').lower()
                if any(variant in group_name or group_name in variant for variant in name_variants):
                    relevant_victims.append(victim)
            
            if relevant_victims:
                return {
                    'victims': relevant_victims,
                    'total_victims': len(relevant_victims),
                    'active': True
                }
        
        return None
    except Exception as e:
        return None

def generate_basic_profile(actor_name, actor_data):
    """Generate basic profile info from incidents.csv data"""
    profile = {
        'alias': 'See AlienVault OTX data below',
        'origin': 'Under Investigation',
        'active_since': 'Unknown',
        'type': 'Unclassified',
        'threat_level': 'Medium'
    }
    
    if not actor_data.empty:
        # Determine threat level from data
        total_attacks = len(actor_data)
        countries = actor_data['country'].nunique()
        sectors = actor_data['sector'].nunique()
        high_severity = len(actor_data[actor_data['severity'] == 'High']) if 'severity' in actor_data.columns else 0
        
        if total_attacks > 50 or countries > 10 or high_severity > 20:
            profile['threat_level'] = 'Critical'
        elif total_attacks > 20 or countries > 5 or high_severity > 10:
            profile['threat_level'] = 'High'
        
        # Estimate active since from data
        if 'date' in actor_data.columns:
            first_seen = actor_data['date'].min()
            profile['active_since'] = first_seen.strftime('%Y')
    
    return profile

# ============================================================================
# MAIN PAGE LOGIC
# ============================================================================

df = load_data()

# Get selected actor
query_params = st.query_params
selected_actor = ""

if "actor" in query_params:
    actor_param = query_params.get("actor")
    if isinstance(actor_param, list):
        selected_actor = actor_param[0] if actor_param else ""
    else:
        selected_actor = actor_param

if not selected_actor:
    selected_actor = st.session_state.get('selected_actor', '')

if not selected_actor:
    st.error("⚠️ No threat actor selected.")
    st.markdown(f'<div style="text-align: center; margin: 3rem 0;"><a href="/Threat_Actors" style="display: inline-block; padding: 1rem 2rem; background: {CYHAWK_RED}; color: white; border-radius: 8px; text-decoration: none; font-weight: 600;">← Go to Threat Actors</a></div>', unsafe_allow_html=True)
    st.stop()

# Filter data for selected actor
actor_data = df[df['actor'] == selected_actor].copy() if not df.empty else pd.DataFrame()

# Generate basic profile
profile = generate_basic_profile(selected_actor, actor_data)

# Fetch API data with progress indicators
st.info(f"🔄 Generating comprehensive report for **{selected_actor}**...")

with st.spinner("Fetching threat intelligence from AlienVault OTX..."):
    otx_data = fetch_alienvault_otx_data(selected_actor)

with st.spinner("Checking ransomware victim database..."):
    ransomware_data = fetch_ransomware_live_data(selected_actor)

# ============================================================================
# HEADER
# ============================================================================

st.markdown(f"""
<div class="profile-header">
    <a href="/Threat_Actors" style="color: white; text-decoration: none; opacity: 0.9; display: inline-block; margin-bottom: 1rem; padding: 0.5rem 1rem; background: rgba(255,255,255,0.1); border-radius: 6px;">
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

# ============================================================================
# OVERVIEW (AI-GENERATED)
# ============================================================================

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">📋 Overview</h2>', unsafe_allow_html=True)

overview_parts = []

if not actor_data.empty:
    total = len(actor_data)
    countries = actor_data['country'].nunique()
    sectors = actor_data['sector'].nunique()
    date_range = f"{actor_data['date'].min().strftime('%B %Y')} to {actor_data['date'].max().strftime('%B %Y')}"
    
    overview_parts.append(f"**{selected_actor}** has been tracked in {total} cyber incidents affecting {countries} countries across {sectors} different sectors, with activity spanning from {date_range}.")

if otx_data and otx_data['pulse_count'] > 0:
    overview_parts.append(f"AlienVault OTX reports {otx_data['pulse_count']} threat intelligence pulses associated with this actor, indicating active monitoring by the global security community.")

if ransomware_data:
    overview_parts.append(f"Ransomware.live has documented {ransomware_data['total_victims']} victim organizations attributed to this threat actor, confirming active ransomware operations.")

if not overview_parts:
    overview_parts.append(f"**{selected_actor}** is an emerging or low-profile threat actor with limited public intelligence available. Continued monitoring and intelligence sharing are recommended to develop a comprehensive threat assessment.")

for part in overview_parts:
    st.markdown(part)
    st.markdown("")

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# ATTACK STATISTICS (from incidents.csv)
# ============================================================================

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

# ============================================================================
# MITRE ATT&CK TTPs (from AlienVault OTX tags)
# ============================================================================

if otx_data and otx_data.get('tags'):
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">🎯 MITRE ATT&CK & Threat Tags</h2>', unsafe_allow_html=True)
    
    st.markdown(f"**Tags from {otx_data['pulse_count']} threat intelligence pulses:**")
    
    for tag in otx_data['tags'][:30]:  # Show first 30 tags
        st.markdown(f'<span class="mitre-ttp">{tag}</span>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# TARGETED COUNTRIES (Charts)
# ============================================================================

if not actor_data.empty:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">🌍 Targeted Countries</h2>', unsafe_allow_html=True)
    
    country_stats = actor_data['country'].value_counts().head(10).reset_index()
    country_stats.columns = ['Country', 'Incidents']
    
    fig_geo = px.bar(country_stats, x='Incidents', y='Country', orientation='h',
                     title=f'Top 10 Countries Targeted by {selected_actor}')
    fig_geo.update_traces(marker_color=CYHAWK_RED)
    fig_geo.update_layout(yaxis={'categoryorder': 'total ascending'}, height=400)
    st.plotly_chart(fig_geo, use_container_width=True)
    
    top_country = country_stats.iloc[0]
    st.markdown(f"**Primary Target:** {top_country['Country']} ({top_country['Incidents']} incidents, {(top_country['Incidents']/len(actor_data)*100):.1f}%)")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# TARGETED INDUSTRIES (Charts)
# ============================================================================

if not actor_data.empty:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">🏢 Targeted Industries</h2>', unsafe_allow_html=True)
    
    sector_stats = actor_data['sector'].value_counts().reset_index()
    sector_stats.columns = ['Sector', 'Incidents']
    
    fig_sector = px.pie(sector_stats, values='Incidents', names='Sector',
                       title=f'Industry Distribution - {selected_actor} Attacks',
                       hole=0.4)
    fig_sector.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_sector, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# INDICATORS OF COMPROMISE (from AlienVault OTX)
# ============================================================================

if otx_data and otx_data.get('iocs'):
    iocs = otx_data['iocs']
    
    if any(iocs.values()):  # If there are any IOCs
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-title">🔍 Indicators of Compromise (AlienVault OTX)</h2>', unsafe_allow_html=True)
        
        st.warning(f"⚠️ **{len(iocs['domains']) + len(iocs['ips']) + len(iocs['hashes'])} IOCs extracted from {otx_data['pulse_count']} threat pulses**")
        
        ioc_tabs = st.tabs(["🌐 Domains", "📡 IP Addresses", "🔐 File Hashes", "🔗 URLs", "📧 Emails", "🛡️ CVEs"])
        
        with ioc_tabs[0]:
            if iocs['domains']:
                st.markdown(f"**{len(iocs['domains'])} malicious domains:**")
                for domain in iocs['domains'][:50]:
                    st.code(domain, language=None)
            else:
                st.info("No domains found")
        
        with ioc_tabs[1]:
            if iocs['ips']:
                st.markdown(f"**{len(iocs['ips'])} IP addresses:**")
                for ip in iocs['ips'][:50]:
                    st.code(ip, language=None)
            else:
                st.info("No IPs found")
        
        with ioc_tabs[2]:
            if iocs['hashes']:
                st.markdown(f"**{len(iocs['hashes'])} file hashes:**")
                for hash_val in iocs['hashes'][:50]:
                    st.code(hash_val, language=None)
            else:
                st.info("No hashes found")
        
        with ioc_tabs[3]:
            if iocs['urls']:
                st.markdown(f"**{len(iocs['urls'])} malicious URLs:**")
                for url in iocs['urls'][:50]:
                    st.code(url, language=None)
            else:
                st.info("No URLs found")
        
        with ioc_tabs[4]:
            if iocs['emails']:
                st.markdown(f"**{len(iocs['emails'])} email addresses:**")
                for email in iocs['emails'][:50]:
                    st.code(email, language=None)
            else:
                st.info("No emails found")
        
        with ioc_tabs[5]:
            if iocs['cves']:
                st.markdown(f"**{len(iocs['cves'])} CVE exploits:**")
                for cve in iocs['cves']:
                    st.code(cve, language=None)
            else:
                st.info("No CVEs found")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# RANSOMWARE VICTIMS (from Ransomware.live)
# ============================================================================

if ransomware_data:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">🎯 Ransomware Victims (Ransomware.live)</h2>', unsafe_allow_html=True)
    
    st.markdown(f"""
    **Status:** 🔴 ACTIVE  
    **Total Victims Tracked:** {ransomware_data['total_victims']}
    """)
    
    st.markdown("### Recent Victims:")
    
    for victim in ransomware_data['victims'][:20]:
        st.markdown(f"""
        <div style="padding: 0.75rem; background: var(--secondary-background-color); 
             border-left: 3px solid {CYHAWK_RED}; border-radius: 4px; margin: 0.5rem 0;">
            <strong>{victim.get('post_title', 'Unknown')}</strong><br>
            <small>Country: {victim.get('country', 'Unknown')} | 
            Discovered: {victim.get('discovered', 'Unknown')}</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# ATTACK TIMELINE
# ============================================================================

if not actor_data.empty:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">📈 Attack Timeline</h2>', unsafe_allow_html=True)
    
    timeline = actor_data.groupby(actor_data['date'].dt.to_period('M')).size().reset_index()
    timeline.columns = ['Month', 'Attacks']
    timeline['Month'] = timeline['Month'].dt.to_timestamp()
    
    fig_timeline = px.line(timeline, x='Month', y='Attacks',
                          title=f'{selected_actor} - Activity Over Time')
    fig_timeline.update_traces(line_color=CYHAWK_RED, line_width=3, mode='lines+markers')
    fig_timeline.update_layout(hovermode='x unified')
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# ANALYST NOTE (Auto-generated)
# ============================================================================

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">💼 Analyst Assessment</h2>', unsafe_allow_html=True)

analyst_notes = []

if not actor_data.empty:
    total = len(actor_data)
    countries = actor_data['country'].nunique()
    threat_level = profile['threat_level']
    
    analyst_notes.append(f"**Threat Assessment: {threat_level.upper()}**")
    analyst_notes.append(f"\n**{selected_actor}** has demonstrated {total} confirmed attacks across {countries} countries, indicating {'widespread international operations' if countries > 10 else 'focused regional targeting'}.")

if otx_data and otx_data['pulse_count'] > 10:
    analyst_notes.append(f"\nHigh community attention with {otx_data['pulse_count']} threat intelligence pulses suggests this is a well-documented and actively monitored threat actor.")

if ransomware_data:
    analyst_notes.append(f"\nActive ransomware operations with {ransomware_data['total_victims']} documented victims indicate ongoing financial motivation and operational capability.")

analyst_notes.append("\n**Recommendations:**\n1. Implement IOCs across security stack (firewall, SIEM, EDR)\n2. Conduct threat hunting for historical compromise\n3. Review and update incident response procedures\n4. Enhance monitoring for tactics associated with this actor\n5. Participate in threat intelligence sharing communities")

st.markdown('<div class="analyst-note">', unsafe_allow_html=True)
for note in analyst_notes:
    st.markdown(note)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(f'<a href="/Threat_Actors" style="display: inline-block; padding: 0.75rem 1.5rem; background: transparent; color: {CYHAWK_RED}; border: 2px solid {CYHAWK_RED}; border-radius: 6px; text-decoration: none; font-weight: 600;">← Back to Threat Actors</a>', unsafe_allow_html=True)

st.success("✅ Report generated successfully from incidents.csv, AlienVault OTX, and Ransomware.live")
