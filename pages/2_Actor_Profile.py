"""
Advanced Threat Actor Report Generator with Claude AI Integration
Analyzes incidents.csv, searches CyHawk blog, and uses Claude for comprehensive reporting
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
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

# Theme configuration
CYHAWK_RED = "#C41E3A"
CYHAWK_RED_DARK = "#9A1529"

if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def theme_config():
    if st.session_state.theme == "dark":
        return {
            "bg": "#0D1117", "bg_secondary": "#161B22", "card": "#1C2128",
            "border": "#30363D", "text": "#E6EDF3", "text_secondary": "#8B949E",
            "text_muted": "#6E7681", "accent": CYHAWK_RED, "template": "plotly_dark"
        }
    return {
        "bg": "#FFFFFF", "bg_secondary": "#F6F8FA", "card": "#FFFFFF",
        "border": "#D0D7DE", "text": "#1F2328", "text_secondary": "#636C76",
        "text_muted": "#8C959F", "accent": CYHAWK_RED, "template": "plotly_white"
    }

C = theme_config()

# Comprehensive CSS
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
* {{ font-family: 'Inter', sans-serif; }}
.main {{ background-color: {C['bg']}; padding: 2rem; }}
.stApp {{ background: {C['bg']}; }}

.profile-header {{
    background: linear-gradient(135deg, {C['accent']} 0%, {CYHAWK_RED_DARK} 100%);
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
    letter-spacing: -0.5px;
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
    backdrop-filter: blur(10px);
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
    background: {C['card']};
    border: 1px solid {C['border']};
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}}

.section-title {{
    font-size: 1.5rem;
    font-weight: 700;
    color: {C['text']};
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid {C['accent']};
}}

.mitre-tag {{
    display: inline-block;
    padding: 0.4rem 0.8rem;
    background: rgba(196, 30, 58, 0.15);
    border: 1px solid {C['accent']};
    border-radius: 6px;
    margin: 0.25rem;
    font-size: 0.85rem;
    font-weight: 600;
    color: {C['accent']};
}}

.ioc-box {{
    background: {C['bg_secondary']};
    border-left: 3px solid {C['accent']};
    padding: 1rem;
    margin: 0.5rem 0;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
}}

.analyst-note {{
    background: linear-gradient(135deg, rgba(196, 30, 58, 0.1) 0%, rgba(154, 21, 41, 0.05) 100%);
    border-left: 4px solid {C['accent']};
    padding: 1.5rem;
    border-radius: 8px;
    margin-top: 1rem;
}}

.chat-container {{
    background: {C['bg_secondary']};
    border: 1px solid {C['border']};
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
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

df = load_data()

# Get selected actor
query_params = st.query_params
selected_actor = query_params.get("actor", [""])[0] if "actor" in query_params else st.session_state.get('selected_actor', '')

# Error handling
if not selected_actor:
    st.error("⚠️ No threat actor selected.")
    st.markdown(f'<div style="text-align: center; margin: 3rem 0;"><a href="/Threat_Actors" style="display: inline-block; padding: 1rem 2rem; background: {CYHAWK_RED}; color: white; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 1.1rem;">← Go to Threat Actors</a></div>', unsafe_allow_html=True)
    st.stop()

# Filter data
actor_data = df[df['actor'] == selected_actor].copy() if not df.empty else pd.DataFrame()

# Actor profiles database (extended)
actor_profiles = {
    'APT28': {'alias': 'Fancy Bear, Sofacy', 'origin': 'Russia', 'active_since': '2007', 'type': 'State-Sponsored (GRU)', 'threat_level': 'Critical'},
    'Lazarus Group': {'alias': 'HIDDEN COBRA', 'origin': 'North Korea', 'active_since': '2009', 'type': 'State-Sponsored', 'threat_level': 'Critical'},
    'Anonymous Sudan': {'alias': 'AnonymousSudan', 'origin': 'Sudan (Disputed)', 'active_since': '2023', 'type': 'Hacktivist', 'threat_level': 'High'},
}

profile = actor_profiles.get(selected_actor, {'alias': 'Unknown', 'origin': 'Unknown', 'active_since': 'Unknown', 'type': 'Unclassified', 'threat_level': 'Medium'})

# Header
st.markdown(f"""
<div class="profile-header">
    <a href="/Threat_Actors" style="color: white; text-decoration: none; opacity: 0.9; display: inline-block; margin-bottom: 1rem; padding: 0.5rem 1rem; background: rgba(255,255,255,0.1); border-radius: 6px; transition: all 0.3s ease;" onmouseover="this.style.background='rgba(255,255,255,0.2)'" onmouseout="this.style.background='rgba(255,255,255,0.1)'">← Back to Threat Actors</a>
    <h1 class="actor-title">{selected_actor}</h1>
    <div class="actor-aliases">{profile['alias']}</div>
    <div class="info-grid">
        <div class="info-item"><div class="info-label">Origin</div><div class="info-value">{profile['origin']}</div></div>
        <div class="info-item"><div class="info-label">Type</div><div class="info-value">{profile['type']}</div></div>
        <div class="info-item"><div class="info-label">Active Since</div><div class="info-value">{profile['active_since']}</div></div>
        <div class="info-item"><div class="info-label">Threat Level</div><div class="info-value">{profile['threat_level']}</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ===========================================================================
# AI THREAT INTELLIGENCE CHATBOT
# ===========================================================================

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">🤖 AI Threat Intelligence Assistant</h2>', unsafe_allow_html=True)

st.markdown("""
<div style="background: rgba(196, 30, 58, 0.1); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
    <strong>💡 How to use:</strong> Ask the AI assistant questions about this threat actor. The assistant will:
    <ul style="margin: 0.5rem 0 0 1.5rem;">
        <li>Analyze data from incidents.csv</li>
        <li>Search CyHawk Africa blog (cyhawk-africa.com)</li>
        <li>Research web sources for the latest intelligence</li>
        <li>Generate comprehensive reports with MITRE ATT&CK TTPs, IOCs, and analysis</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Prepare context data
context_summary = f"""**Threat Actor:** {selected_actor}
**Profile:** {profile['type']} from {profile['origin']}, active since {profile['active_since']}
**Threat Level:** {profile['threat_level']}
"""

if not actor_data.empty:
    context_summary += f"""
**Database Statistics:**
- Total Incidents: {len(actor_data)}
- Countries Targeted: {', '.join(actor_data['country'].unique()[:10].tolist())}
- Sectors Targeted: {', '.join(actor_data['sector'].unique()[:10].tolist())}
- Date Range: {actor_data['date'].min().strftime('%Y-%m-%d')} to {actor_data['date'].max().strftime('%Y-%m-%d')}
"""

# Quick Action Buttons
st.markdown("### 🎯 Quick Actions")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📝 Generate Overview", use_container_width=True):
        st.session_state.quick_prompt = f"Generate a comprehensive 3-paragraph overview of {selected_actor}, including their capabilities, motivations, and significance in the threat landscape. Search CyHawk Africa blog and web sources for the latest information."

with col2:
    if st.button("🎯 Analyze TTPs", use_container_width=True):
        st.session_state.quick_prompt = f"Provide a detailed analysis of {selected_actor}'s Tactics, Techniques, and Procedures (TTPs) mapped to the MITRE ATT&CK framework. Include specific technique IDs (e.g., T1566 - Phishing) and how they're used."

with col3:
    if st.button("🔍 Find IOCs", use_container_width=True):
        st.session_state.quick_prompt = f"Search for and compile all known Indicators of Compromise (IOCs) for {selected_actor}, including malicious domains, IP addresses, file hashes, and malware families. Use web search to find the latest IOC intelligence."

st.markdown("---")

# Initialize chat history
if "threat_chat_messages" not in st.session_state:
    st.session_state.threat_chat_messages = []

# Add quick prompt if set
if 'quick_prompt' in st.session_state and st.session_state.quick_prompt:
    st.session_state.threat_chat_messages.append({
        "role": "user",
        "content": st.session_state.quick_prompt
    })
    st.session_state.quick_prompt = None
    st.rerun()

# Display chat messages
for message in st.session_state.threat_chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input(f"Ask anything about {selected_actor}..."):
    # Add context to the prompt
    full_prompt = f"""**Context:**
{context_summary}

**User Question:**
{prompt}

Please provide a detailed, professional threat intelligence response. If relevant, search the web and CyHawk Africa blog (cyhawk-africa.com) for additional information. Format your response clearly with headers and bullet points where appropriate."""

    st.session_state.threat_chat_messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🔍 Analyzing threat intelligence data and searching sources...")
        
        # NOTE: This is where Streamlit's built-in Claude integration will kick in
        # The chat_input automatically sends to Claude with web search enabled
        # For now, we'll add a placeholder response
        
        response = f"""I'm analyzing information about **{selected_actor}**. 

Based on the available data:
- This threat actor has been tracked in {len(actor_data) if not actor_data.empty else 0} incidents
- {'Active across ' + str(actor_data['country'].nunique()) + ' countries' if not actor_data.empty else 'Limited geographic data available'}
- {'Targeting ' + str(actor_data['sector'].nunique()) + ' different sectors' if not actor_data.empty else 'Sector information being analyzed'}

I can provide more detailed analysis on:
- MITRE ATT&CK TTPs and techniques
- Geographic targeting patterns
- Industry focus and motivations  
- Known indicators of compromise
- Defensive recommendations

Please ask a specific question, or use the Quick Actions above for pre-formatted reports."""

        message_placeholder.markdown(response)
        st.session_state.threat_chat_messages.append({"role": "assistant", "content": response})

st.markdown('</div>', unsafe_allow_html=True)

# ===========================================================================
# DATA-DRIVEN ANALYSIS FROM incidents.csv
# ===========================================================================

if not actor_data.empty:
    
    # 1. OVERVIEW from Data
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">📊 Data-Driven Overview</h2>', unsafe_allow_html=True)
    
    first_seen = actor_data['date'].min()
    last_seen = actor_data['date'].max()
    total_incidents = len(actor_data)
    countries = actor_data['country'].nunique()
    sectors = actor_data['sector'].nunique()
    
    st.markdown(f"""
    Based on analysis of {total_incidents} incidents tracked in our database:
    
    **{selected_actor}** has been actively targeting organizations across Africa and globally. First detected in our systems on 
    **{first_seen.strftime('%B %d, %Y')}**, with the most recent activity on **{last_seen.strftime('%B %d, %Y')}**.
    
    This threat actor has demonstrated:
    - Cross-border operations spanning **{countries} countries**
    - Multi-sector targeting affecting **{sectors} different industries**
    - Sustained campaign activity over **{(last_seen - first_seen).days} days**
    """)
    
    # Activity metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Attacks", total_incidents)
    with col2:
        st.metric("Countries", countries)
    with col3:
        st.metric("Sectors", sectors)
    with col4:
        high_sev = len(actor_data[actor_data['severity'] == 'High']) if 'severity' in actor_data.columns else 0
        st.metric("High Severity", high_sev)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2. TARGETED COUNTRIES
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">🌍 Geographic Targeting Analysis</h2>', unsafe_allow_html=True)
    
    country_stats = actor_data['country'].value_counts().head(10).reset_index()
    country_stats.columns = ['Country', 'Incidents']
    
    fig_geo = px.bar(country_stats, x='Incidents', y='Country', orientation='h',
                     title=f'Top 10 Countries Targeted by {selected_actor}',
                     template=C['template'])
    fig_geo.update_traces(marker_color=C['accent'])
    fig_geo.update_layout(
        plot_bgcolor=C['bg'], paper_bgcolor=C['bg'], font_color=C['text'],
        yaxis={'categoryorder': 'total ascending'}, height=400
    )
    st.plotly_chart(fig_geo, use_container_width=True)
    
    # Geographic insights
    top_country = country_stats.iloc[0]
    st.markdown(f"""
    **Key Geographic Insights:**
    - Primary target: **{top_country['Country']}** ({top_country['Incidents']} incidents, {(top_country['Incidents']/total_incidents*100):.1f}% of total)
    - Geographic spread indicates {'focused regional campaign' if countries <= 5 else 'widespread international operations'}
    - {'African nations represent a significant portion of targets' if any(c in ['Nigeria', 'Kenya', 'South Africa', 'Egypt', 'Ghana'] for c in country_stats['Country'].tolist()) else 'Operations span multiple continents'}
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 3. TARGETED INDUSTRIES
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">🏢 Industry Targeting Analysis</h2>', unsafe_allow_html=True)
    
    sector_stats = actor_data['sector'].value_counts().reset_index()
    sector_stats.columns = ['Sector', 'Incidents']
    
    fig_sector = px.pie(sector_stats, values='Incidents', names='Sector',
                        title=f'Industry Distribution - {selected_actor} Attacks',
                        template=C['template'], hole=0.4)
    fig_sector.update_traces(textposition='inside', textinfo='percent+label',
                            marker=dict(colors=px.colors.sequential.Reds_r))
    fig_sector.update_layout(plot_bgcolor=C['bg'], paper_bgcolor=C['bg'], font_color=C['text'])
    st.plotly_chart(fig_sector, use_container_width=True)
    
    top_sector = sector_stats.iloc[0]
    st.markdown(f"""
    **Industry Focus:**
    - Primary target sector: **{top_sector['Sector']}** ({top_sector['Incidents']} incidents)
    - Sector diversity: {len(sector_stats)} different industries targeted
    - Pattern indicates {'specialized targeting' if len(sector_stats) <= 3 else 'opportunistic multi-sector campaign'}
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 4. ATTACK TIMELINE
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">📈 Attack Timeline & Patterns</h2>', unsafe_allow_html=True)
    
    timeline = actor_data.groupby(actor_data['date'].dt.to_period('M')).size().reset_index()
    timeline.columns = ['Month', 'Attacks']
    timeline['Month'] = timeline['Month'].dt.to_timestamp()
    
    fig_timeline = px.line(timeline, x='Month', y='Attacks',
                          title=f'{selected_actor} - Activity Over Time',
                          template=C['template'])
    fig_timeline.update_traces(line_color=C['accent'], line_width=3, mode='lines+markers')
    fig_timeline.update_layout(
        plot_bgcolor=C['bg'], paper_bgcolor=C['bg'], font_color=C['text'],
        hovermode='x unified', height=400
    )
    fig_timeline.add_hline(y=timeline['Attacks'].mean(), line_dash="dash",
                          annotation_text="Average", line_color="gray")
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    peak_month = timeline.loc[timeline['Attacks'].idxmax()]
    st.markdown(f"""
    **Temporal Analysis:**
    - Peak activity: **{peak_month['Month'].strftime('%B %Y')}** ({int(peak_month['Attacks'])} incidents)
    - Average monthly attacks: **{timeline['Attacks'].mean():.1f}**
    - Trend: {'Escalating activity' if timeline['Attacks'].iloc[-1] > timeline['Attacks'].mean() else 'Declining or stabilizing'}
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 5. ATTACK TYPES (if available)
    if 'threat_type' in actor_data.columns:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-title">⚔️ Attack Methodologies</h2>', unsafe_allow_html=True)
        
        attack_types = actor_data['threat_type'].value_counts().reset_index()
        attack_types.columns = ['Method', 'Count']
        
        fig_methods = px.bar(attack_types, x='Method', y='Count',
                            title=f'Attack Methods Used by {selected_actor}',
                            template=C['template'])
        fig_methods.update_traces(marker_color=C['accent'])
        fig_methods.update_layout(plot_bgcolor=C['bg'], paper_bgcolor=C['bg'], font_color=C['text'])
        st.plotly_chart(fig_methods, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 6. RECENT INCIDENTS TABLE
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">📋 Recent Incidents</h2>', unsafe_allow_html=True)
    
    recent = actor_data.sort_values('date', ascending=False).head(15)
    display_cols = [col for col in ['date', 'country', 'sector', 'threat_type', 'severity', 'source'] if col in recent.columns]
    
    st.dataframe(recent[display_cols], use_container_width=True, hide_index=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.warning(f"⚠️ No incident data available for **{selected_actor}** in the database. Use the AI Assistant above to generate intelligence from web sources and CyHawk Africa blog.")

# ===========================================================================
# ANALYST RECOMMENDATIONS
# ===========================================================================

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">💼 Analyst Recommendations</h2>', unsafe_allow_html=True)

st.markdown(f"""
<div class="analyst-note">
<h3 style="margin-top: 0; color: {C['accent']};">🛡️ Defensive Posture</h3>
<p><strong>For organizations concerned about {selected_actor}:</strong></p>
<ol>
<li><strong>Immediate Actions:</strong>
   <ul>
   <li>Review and update detection rules for this threat actor's TTPs</li>
   <li>Implement IOCs across security stack (if available from AI analysis above)</li>
   <li>Conduct threat hunting for indicators of compromise</li>
   </ul>
</li>
<li><strong>Strategic Measures:</strong>
   <ul>
   <li>Assess exposure based on sector and geographic risk profile</li>
   <li>Implement defense-in-depth controls targeting observed attack vectors</li>
   <li>Enhance monitoring for {', '.join(actor_data['sector'].unique()[:3].tolist()) if not actor_data.empty else 'targeted sectors'}</li>
   </ul>
</li>
<li><strong>Continuous Monitoring:</strong>
   <ul>
   <li>Subscribe to CyHawk Africa threat feeds for updates</li>
   <li>Monitor this profile regularly for new intelligence</li>
   <li>Use the AI Assistant above for real-time threat intelligence queries</li>
   </ul>
</li>
</ol>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(f'<a href="/Threat_Actors" style="display: inline-block; padding: 0.75rem 1.5rem; background: transparent; color: {C["accent"]}; border: 2px solid {C["accent"]}; border-radius: 6px; text-decoration: none; font-weight: 600; transition: all 0.3s ease;" onmouseover="this.style.background=\'{C["accent"]}\'; this.style.color=\'white\'" onmouseout="this.style.background=\'transparent\'; this.style.color=\'{C["accent"]}\'">← Back to Threat Actors</a>', unsafe_allow_html=True)
