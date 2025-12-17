"""
CyHawk Africa – Comprehensive Threat Actor Profile
Features:
- Dark/Light mode support
- incidents.csv analysis
- ransomware.live enrichment
- MITRE ATT&CK TTP mapping
- Risk scoring
- PDF export
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests
import os
import json
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

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

# Theme colors
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

.ttp-badge {{
    display: inline-block;
    padding: 0.5rem 1rem;
    background: rgba(196, 30, 58, 0.1);
    border: 1px solid {CYHAWK_RED};
    border-radius: 6px;
    margin: 0.25rem;
    font-size: 0.9rem;
}}

.risk-meter {{
    text-align: center;
    padding: 2rem;
    border-radius: 12px;
    margin: 1rem 0;
}}

.risk-critical {{
    background: linear-gradient(135deg, rgba(220, 38, 38, 0.2), rgba(185, 28, 28, 0.1));
    border: 2px solid #DC2626;
}}

.risk-high {{
    background: linear-gradient(135deg, rgba(249, 115, 22, 0.2), rgba(234, 88, 12, 0.1));
    border: 2px solid #F97316;
}}

.risk-medium {{
    background: linear-gradient(135deg, rgba(234, 179, 8, 0.2), rgba(202, 138, 4, 0.1));
    border: 2px solid #EAB308;
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
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

@st.cache_data
def load_incidents():
    """Load incidents from CSV"""
    if not os.path.exists("data/incidents.csv"):
        return pd.DataFrame()
    df = pd.read_csv("data/incidents.csv")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df.dropna(subset=["date"])

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_ransomware_live_comprehensive(actor_name):
    """
    Fetch comprehensive ransomware intelligence from ransomware.live
    Tries multiple endpoints for complete intelligence
    """
    base = "https://api.ransomware.live"
    result = {
        'group_info': None,
        'victims': [],
        'negotiations': [],
        'iocs': [],
        'ransom_notes': [],
        'yara_rules': []
    }
    
    # Normalize actor name for API
    actor_normalized = actor_name.lower().replace(' ', '').replace('-', '').replace('_', '')
    
    # Try to get group information
    endpoints = [
        f"/groups",
        f"/recentvictims",
        f"/group/{actor_normalized}",
    ]
    
    # Get recent victims and filter
    try:
        response = requests.get(f"{base}/recentvictims", timeout=15)
        if response.status_code == 200:
            all_victims = response.json()
            
            # Filter victims for this actor
            name_variants = [
                actor_name.lower(),
                actor_name.replace(' ', '').lower(),
                actor_name.replace(' ', '-').lower(),
                actor_name.replace('-', '').lower()
            ]
            
            for victim in all_victims:
                group_name = victim.get('group_name', '').lower()
                if any(variant in group_name or group_name in variant for variant in name_variants):
                    result['victims'].append(victim)
    except:
        pass
    
    # Try to get group-specific data
    try:
        response = requests.get(f"{base}/group/{actor_normalized}", timeout=15)
        if response.status_code == 200:
            result['group_info'] = response.json()
    except:
        pass
    
    return result if (result['victims'] or result['group_info']) else None

# ============================================================================
# MITRE ATT&CK TTP MAPPING
# ============================================================================

def infer_mitre_ttps(actor_name, incidents_df, ransomware_data):
    """
    Infer MITRE ATT&CK TTPs based on:
    - Actor name patterns
    - Incident characteristics
    - Ransomware operations
    """
    ttps = []
    
    # Check for ransomware keywords
    ransomware_keywords = ['ransomware', 'lockbit', 'revil', 'darkside', 'conti', 'maze', 'blackcat']
    is_ransomware = any(kw in actor_name.lower() for kw in ransomware_keywords)
    
    if is_ransomware or (ransomware_data and ransomware_data.get('victims')):
        ttps.extend([
            {'id': 'T1486', 'name': 'Data Encrypted for Impact', 'tactic': 'Impact'},
            {'id': 'T1490', 'name': 'Inhibit System Recovery', 'tactic': 'Impact'},
            {'id': 'T1567', 'name': 'Exfiltration Over Web Service', 'tactic': 'Exfiltration'},
            {'id': 'T1041', 'name': 'Exfiltration Over C2 Channel', 'tactic': 'Exfiltration'},
            {'id': 'T1566.001', 'name': 'Spearphishing Attachment', 'tactic': 'Initial Access'},
        ])
    
    if not incidents_df.empty:
        # Multiple sectors = sophisticated targeting
        if incidents_df['sector'].nunique() > 3:
            ttps.append({'id': 'T1589', 'name': 'Gather Victim Identity Information', 'tactic': 'Reconnaissance'})
            ttps.append({'id': 'T1590', 'name': 'Gather Victim Network Information', 'tactic': 'Reconnaissance'})
        
        # Multiple countries = infrastructure
        if incidents_df['country'].nunique() > 5:
            ttps.append({'id': 'T1583', 'name': 'Acquire Infrastructure', 'tactic': 'Resource Development'})
            ttps.append({'id': 'T1584', 'name': 'Compromise Infrastructure', 'tactic': 'Resource Development'})
        
        # High severity attacks = privilege escalation
        if 'severity' in incidents_df.columns and len(incidents_df[incidents_df['severity'] == 'High']) > 5:
            ttps.append({'id': 'T1078', 'name': 'Valid Accounts', 'tactic': 'Privilege Escalation'})
            ttps.append({'id': 'T1068', 'name': 'Exploitation for Privilege Escalation', 'tactic': 'Privilege Escalation'})
    
    # Common TTPs for any threat actor
    ttps.extend([
        {'id': 'T1059', 'name': 'Command and Scripting Interpreter', 'tactic': 'Execution'},
        {'id': 'T1027', 'name': 'Obfuscated Files or Information', 'tactic': 'Defense Evasion'},
        {'id': 'T1082', 'name': 'System Information Discovery', 'tactic': 'Discovery'},
        {'id': 'T1005', 'name': 'Data from Local System', 'tactic': 'Collection'},
    ])
    
    # Remove duplicates
    seen = set()
    unique_ttps = []
    for ttp in ttps:
        if ttp['id'] not in seen:
            seen.add(ttp['id'])
            unique_ttps.append(ttp)
    
    return unique_ttps

# ============================================================================
# RISK SCORING ENGINE
# ============================================================================

def calculate_comprehensive_risk_score(incidents_df, ransomware_data):
    """
    Calculate comprehensive risk score (0-100)
    Based on multiple threat indicators
    """
    score = 0
    breakdown = {}
    
    # 1. Incident Volume (0-25 points)
    incident_count = len(incidents_df) if not incidents_df.empty else 0
    incident_score = min(incident_count * 0.5, 25)
    score += incident_score
    breakdown['Incident Volume'] = incident_score
    
    # 2. Geographic Spread (0-20 points)
    if not incidents_df.empty:
        countries = incidents_df['country'].nunique()
        geo_score = min(countries * 2, 20)
        score += geo_score
        breakdown['Geographic Spread'] = geo_score
    
    # 3. Sector Targeting (0-15 points)
    if not incidents_df.empty:
        sectors = incidents_df['sector'].nunique()
        sector_score = min(sectors * 2.5, 15)
        score += sector_score
        breakdown['Sector Diversity'] = sector_score
    
    # 4. Attack Severity (0-20 points)
    if not incidents_df.empty and 'severity' in incidents_df.columns:
        high_severity = len(incidents_df[incidents_df['severity'] == 'High'])
        severity_score = min(high_severity * 1.5, 20)
        score += severity_score
        breakdown['Attack Severity'] = severity_score
    
    # 5. Ransomware Operations (0-20 points)
    if ransomware_data:
        ransom_score = 0
        if ransomware_data.get('victims'):
            ransom_score += min(len(ransomware_data['victims']) * 0.5, 15)
        if ransomware_data.get('group_info'):
            ransom_score += 5
        score += ransom_score
        breakdown['Ransomware Activity'] = ransom_score
    
    return min(score, 100), breakdown

def get_risk_classification(score):
    """Classify risk based on score"""
    if score >= 70:
        return "CRITICAL", "risk-critical", "#DC2626"
    elif score >= 40:
        return "HIGH", "risk-high", "#F97316"
    elif score >= 20:
        return "MEDIUM", "risk-medium", "#EAB308"
    else:
        return "LOW", "risk-low", "#10B981"

# ============================================================================
# PDF EXPORT FUNCTIONALITY
# ============================================================================

def generate_pdf_report(actor_name, profile_data, incidents_df, ransomware_data, risk_score, ttps):
    """Generate comprehensive PDF threat brief"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#C41E3A'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#C41E3A'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    # Title
    story.append(Paragraph(f"THREAT ACTOR INTELLIGENCE BRIEF", title_style))
    story.append(Paragraph(f"{actor_name}", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Metadata
    story.append(Paragraph(f"Classification: {profile_data['classification']}", styles['Normal']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}", styles['Normal']))
    story.append(Paragraph(f"Source: CyHawk Africa Threat Intelligence Platform", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Risk Score
    story.append(Paragraph("RISK ASSESSMENT", heading_style))
    risk_class, _, _ = get_risk_classification(risk_score)
    story.append(Paragraph(f"<b>Risk Score:</b> {risk_score}/100 ({risk_class})", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Overview
    story.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
    if not incidents_df.empty:
        overview = f"""
        <b>{actor_name}</b> has been linked to <b>{len(incidents_df)} confirmed incidents</b> 
        affecting <b>{incidents_df['country'].nunique()} countries</b> across 
        <b>{incidents_df['sector'].nunique()} industry sectors</b>. 
        """
        if ransomware_data and ransomware_data.get('victims'):
            overview += f"Ransomware operations have compromised <b>{len(ransomware_data['victims'])} victim organizations</b>."
        story.append(Paragraph(overview, styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # MITRE ATT&CK TTPs
    story.append(Paragraph("MITRE ATT&CK TACTICS & TECHNIQUES", heading_style))
    if ttps:
        ttp_data = [[ttp['id'], ttp['name'], ttp['tactic']] for ttp in ttps[:10]]
        ttp_table = Table([['ID', 'Technique', 'Tactic']] + ttp_data, colWidths=[1*inch, 3*inch, 1.5*inch])
        ttp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C41E3A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(ttp_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Geographic Targeting
    if not incidents_df.empty:
        story.append(Paragraph("GEOGRAPHIC TARGETING", heading_style))
        countries = incidents_df['country'].value_counts().head(5)
        for country, count in countries.items():
            story.append(Paragraph(f"• {country}: {count} incidents", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
    
    # Recommendations
    story.append(Paragraph("DEFENSIVE RECOMMENDATIONS", heading_style))
    recommendations = [
        "Implement advanced endpoint detection and response (EDR) solutions",
        "Conduct threat hunting for indicators associated with this actor",
        "Review and update incident response procedures",
        "Enhance monitoring for TTPs identified in this brief",
        "Participate in threat intelligence sharing communities",
    ]
    for rec in recommendations:
        story.append(Paragraph(f"• {rec}", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

# ============================================================================
# MAIN PAGE
# ============================================================================

# Get actor from query params
query_params = st.query_params
selected_actor = ""

if "actor" in query_params:
    actor_param = query_params.get("actor")
    if isinstance(actor_param, list):
        selected_actor = actor_param[0] if actor_param else ""
    else:
        selected_actor = actor_param

if not selected_actor:
    st.error("⚠️ No threat actor selected.")
    st.markdown(f'<div style="text-align: center;"><a href="/Threat_Actors" style="display: inline-block; padding: 1rem 2rem; background: {CYHAWK_RED}; color: white; border-radius: 8px; text-decoration: none; font-weight: 600;">← Go to Threat Actors</a></div>', unsafe_allow_html=True)
    st.stop()

# Load data
with st.spinner("Loading threat intelligence..."):
    incidents_df = load_incidents()
    actor_df = incidents_df[incidents_df['actor'] == selected_actor] if not incidents_df.empty else pd.DataFrame()
    ransomware_data = fetch_ransomware_live_comprehensive(selected_actor)

# Calculate risk score and TTPs
risk_score, risk_breakdown = calculate_comprehensive_risk_score(actor_df, ransomware_data)
risk_class, risk_css, risk_color = get_risk_classification(risk_score)
ttps = infer_mitre_ttps(selected_actor, actor_df, ransomware_data)

# Prepare profile data
profile_data = {
    'classification': risk_class,
    'origin': 'Under Investigation',
    'active_since': actor_df['date'].min().strftime('%Y') if not actor_df.empty else 'Unknown',
    'type': 'Ransomware Group' if ransomware_data else 'Unclassified'
}

# ============================================================================
# HEADER
# ============================================================================

st.markdown(f"""
<div class="profile-header">
    <a href="/Threat_Actors" style="color: white; text-decoration: none; opacity: 0.9; display: inline-block; margin-bottom: 1rem; padding: 0.5rem 1rem; background: rgba(255,255,255,0.1); border-radius: 6px;">
        ← Back to Threat Actors
    </a>
    <h1 class="actor-title">{selected_actor}</h1>
    <p style="opacity: 0.95; font-size: 1.1rem; margin-top: 0.5rem;">Comprehensive Threat Actor Intelligence Profile</p>
    <div class="info-grid">
        <div class="info-item">
            <div class="info-label">Risk Classification</div>
            <div class="info-value" style="color: {risk_color};">{risk_class}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Type</div>
            <div class="info-value">{profile_data['type']}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Active Since</div>
            <div class="info-value">{profile_data['active_since']}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Incidents Tracked</div>
            <div class="info-value">{len(actor_df)}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# EXPORT BUTTONS
# ============================================================================

col1, col2, col3 = st.columns([1, 1, 4])

with col1:
    if st.button("📄 Export PDF", use_container_width=True):
        pdf_buffer = generate_pdf_report(selected_actor, profile_data, actor_df, ransomware_data, risk_score, ttps)
        st.download_button(
            label="⬇️ Download PDF",
            data=pdf_buffer,
            file_name=f"CyHawk_ThreatBrief_{selected_actor}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

with col2:
    if st.button("📊 Export Data", use_container_width=True):
        export_data = {
            'actor': selected_actor,
            'risk_score': risk_score,
            'risk_classification': risk_class,
            'incidents': len(actor_df),
            'countries': actor_df['country'].nunique() if not actor_df.empty else 0,
            'sectors': actor_df['sector'].nunique() if not actor_df.empty else 0,
            'ttps': [f"{t['id']}: {t['name']}" for t in ttps],
            'generated': datetime.now().isoformat()
        }
        st.download_button(
            label="⬇️ Download JSON",
            data=json.dumps(export_data, indent=2),
            file_name=f"CyHawk_Data_{selected_actor}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )

# ============================================================================
# RISK SCORE SECTION
# ============================================================================

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">🎯 Risk Assessment</h2>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown(f"""
    <div class="risk-meter {risk_css}">
        <div style="font-size: 3rem; font-weight: 800; color: {risk_color};">{risk_score}</div>
        <div style="font-size: 1.2rem; font-weight: 600; color: {risk_color};">/ 100</div>
        <div style="font-size: 1.5rem; font-weight: 700; margin-top: 1rem; color: {risk_color};">{risk_class}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("**Risk Score Breakdown:**")
    for factor, score in risk_breakdown.items():
        percentage = (score / 100) * 100
        st.markdown(f"**{factor}:** {score:.1f} points")
        st.progress(score / 100)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# OVERVIEW
# ============================================================================

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">📋 Executive Summary</h2>', unsafe_allow_html=True)

if not actor_df.empty:
    st.markdown(f"""
**{selected_actor}** has been linked to **{len(actor_df)} confirmed cyber incidents** affecting 
**{actor_df['country'].nunique()} countries** across **{actor_df['sector'].nunique()} industry sectors**.

Activity spans from **{actor_df['date'].min().strftime('%B %Y')}** to **{actor_df['date'].max().strftime('%B %Y')}**, 
indicating sustained operational capability.
""")
    
    if ransomware_data and ransomware_data.get('victims'):
        st.markdown(f"""
**Ransomware Operations:** {len(ransomware_data['victims'])} documented victim organizations, 
confirming active double-extortion tactics and financial motivation.
""")
else:
    st.markdown(f"""
**{selected_actor}** is tracked through external intelligence sources. 
Limited confirmed incident telemetry within CyHawk datasets suggests either emerging operations or high operational security.
""")

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# MITRE ATT&CK TTPs
# ============================================================================

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">🎯 MITRE ATT&CK Tactics & Techniques</h2>', unsafe_allow_html=True)

st.markdown(f"**{len(ttps)} techniques identified** based on operational analysis:")

# Group by tactic
tactics = {}
for ttp in ttps:
    tactic = ttp['tactic']
    if tactic not in tactics:
        tactics[tactic] = []
    tactics[tactic].append(ttp)

for tactic, techniques in sorted(tactics.items()):
    st.markdown(f"### {tactic}")
    for tech in techniques:
        st.markdown(f'<span class="ttp-badge"><strong>{tech["id"]}</strong>: {tech["name"]}</span>', unsafe_allow_html=True)
    st.markdown("")

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# STATISTICS
# ============================================================================

if not actor_df.empty:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">📊 Attack Statistics</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Attacks", len(actor_df))
    with col2:
        st.metric("Countries", actor_df['country'].nunique())
    with col3:
        st.metric("Sectors", actor_df['sector'].nunique())
    with col4:
        high_sev = len(actor_df[actor_df['severity'] == 'High']) if 'severity' in actor_df.columns else 0
        st.metric("High Severity", high_sev)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# TARGETED COUNTRIES
# ============================================================================

if not actor_df.empty:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">🌍 Targeted Countries</h2>', unsafe_allow_html=True)
    
    country_stats = actor_df['country'].value_counts().head(10).reset_index()
    country_stats.columns = ['Country', 'Incidents']
    
    fig_geo = px.bar(country_stats, x='Incidents', y='Country', orientation='h',
                     title=f'Top 10 Countries Targeted by {selected_actor}')
    fig_geo.update_traces(marker_color=CYHAWK_RED)
    fig_geo.update_layout(yaxis={'categoryorder': 'total ascending'}, height=400)
    st.plotly_chart(fig_geo, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# TARGETED INDUSTRIES
# ============================================================================

if not actor_df.empty:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">🏢 Targeted Industries</h2>', unsafe_allow_html=True)
    
    sector_stats = actor_df['sector'].value_counts().reset_index()
    sector_stats.columns = ['Sector', 'Incidents']
    
    fig_sector = px.pie(sector_stats, values='Incidents', names='Sector',
                       title=f'Industry Distribution', hole=0.4)
    fig_sector.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_sector, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# RANSOMWARE INTELLIGENCE
# ============================================================================

if ransomware_data and ransomware_data.get('victims'):
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">🎯 Ransomware Intelligence (ransomware.live)</h2>', unsafe_allow_html=True)
    
    st.markdown(f"""
    **Status:** 🔴 ACTIVE RANSOMWARE OPERATIONS  
    **Victims Documented:** {len(ransomware_data['victims'])}
    """)
    
    st.markdown("### Recent Victims")
    
    for victim in ransomware_data['victims'][:15]:
        st.markdown(f"""
        <div class="ioc-code">
            <strong>{victim.get('post_title', 'Unknown Organization')}</strong><br>
            Country: {victim.get('country', 'Unknown')} | 
            Discovered: {victim.get('discovered', 'Unknown')}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# TIMELINE
# ============================================================================

if not actor_df.empty:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">📈 Activity Timeline</h2>', unsafe_allow_html=True)
    
    timeline = actor_df.groupby(actor_df['date'].dt.to_period('M')).size().reset_index()
    timeline.columns = ['Month', 'Incidents']
    timeline['Month'] = timeline['Month'].dt.to_timestamp()
    
    fig_timeline = px.line(timeline, x='Month', y='Incidents',
                          title=f'{selected_actor} - Attack Frequency Over Time')
    fig_timeline.update_traces(line_color=CYHAWK_RED, line_width=3, mode='lines+markers')
    fig_timeline.update_layout(hovermode='x unified')
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# ANALYST ASSESSMENT
# ============================================================================

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">💼 Analyst Assessment</h2>', unsafe_allow_html=True)

st.markdown(f"""
**Overall Risk Classification:** {risk_class}

**{selected_actor}** demonstrates a comprehensive risk score of **{risk_score}/100**, 
driven by incident frequency, geographic spread, and operational indicators.

""")

if ransomware_data:
    st.markdown("""
**Ransomware Operations:** The presence of documented victims and infrastructure indicates 
sustained ransomware capability with financial motivation. Double-extortion tactics suggest 
data theft precedes encryption.
""")

st.markdown("""
**Defensive Recommendations:**
1. Implement detection rules for identified TTPs
2. Conduct threat hunting for historical compromise indicators
3. Review and enhance backup and recovery procedures
4. Deploy advanced endpoint detection and response (EDR)
5. Participate in threat intelligence sharing communities
""")

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
col1, col2 = st.columns([1, 5])
with col1:
    st.markdown(f'<a href="/Threat_Actors" style="display: inline-block; padding: 0.75rem 1.5rem; background: transparent; color: {CYHAWK_RED}; border: 2px solid {CYHAWK_RED}; border-radius: 6px; text-decoration: none; font-weight: 600;">← Back</a>', unsafe_allow_html=True)
with col2:
    st.success(f"✅ Comprehensive threat intelligence report generated for {selected_actor}")
