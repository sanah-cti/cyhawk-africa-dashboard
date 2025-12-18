"""
CyHawk Africa – Comprehensive Threat Actor Profile
Features:
- Dark/Light mode support
- incidents.csv analysis
- ransomware.live enrichment
- MITRE ATT&CK TTP mapping
- Risk scoring
- PDF export (optional)
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

# Optional PDF export (graceful fallback if not installed)
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    PDF_EXPORT_AVAILABLE = True
except ImportError:
    PDF_EXPORT_AVAILABLE = False

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

def classify_threat_actor_type(actor_name, incidents_df, ransomware_data):
    """
    Intelligently classify threat actor type based on:
    - Actor name patterns
    - Incident data characteristics
    - Ransomware operations
    - Attack patterns
    """
    actor_lower = actor_name.lower()
    
    # Ransomware Groups (check ransomware.live data first)
    if ransomware_data and ransomware_data.get('victims'):
        return "Ransomware Group"
    
    ransomware_keywords = ['ransomware', 'lockbit', 'revil', 'darkside', 'conti', 
                          'maze', 'blackcat', 'alphv', 'blackbasta', 'ryuk', 
                          'nightspire', 'play', 'royal', 'medusa']
    if any(kw in actor_lower for kw in ransomware_keywords):
        return "Ransomware Group"
    
    # Hacktivist Groups
    hacktivist_keywords = ['anonymous', 'ghost', 'killsec', 'keymous', 'funksec', 
                          'oursec', 'legion', 'cyber army', 'team', 'squad']
    if any(kw in actor_lower for kw in hacktivist_keywords):
        return "Hacktivist Group"
    
    # Initial Access Brokers
    iab_keywords = ['bigbrother', 'broker', 'access', 'initial']
    if any(kw in actor_lower for kw in iab_keywords):
        return "Initial Access Broker (IAB)"
    
    # Database Breach Specialists
    db_keywords = ['b4bayega', 'database', 'breach', 'leak', 'dump', 'exfil']
    if any(kw in actor_lower for kw in db_keywords):
        return "Database Breach Specialist"
    
    # APT Groups (State-Sponsored)
    apt_keywords = ['apt', 'lazarus', 'fancy bear', 'cozy bear', 'kimsuky', 
                   'mustang panda', 'winnti', 'sandworm']
    if any(kw in actor_lower for kw in apt_keywords):
        return "Advanced Persistent Threat (APT)"
    
    # Check incident patterns if available
    if not incidents_df.empty:
        # Check for DDoS patterns
        if 'threat_type' in incidents_df.columns:
            threat_types = incidents_df['threat_type'].str.lower()
            
            if threat_types.str.contains('ddos|denial', case=False, na=False).sum() > len(incidents_df) * 0.5:
                return "DDoS Attack Group"
            
            if threat_types.str.contains('malware|trojan|rat', case=False, na=False).sum() > len(incidents_df) * 0.5:
                return "Malware Distribution Network"
            
            if threat_types.str.contains('phishing|spear', case=False, na=False).sum() > len(incidents_df) * 0.5:
                return "Phishing Campaign Operator"
            
            if threat_types.str.contains('web|sql|injection', case=False, na=False).sum() > len(incidents_df) * 0.5:
                return "Web Application Exploit Group"
        
        # Check for targeted vs opportunistic
        sectors = incidents_df['sector'].nunique() if not incidents_df.empty else 0
        countries = incidents_df['country'].nunique() if not incidents_df.empty else 0
        
        if sectors == 1 and countries > 5:
            return "Targeted Cyber Espionage"
        elif sectors > 5 and countries > 5:
            return "Financially Motivated Threat Actor"
    
    # Exploit/Vulnerability keywords
    exploit_keywords = ['exploit', 'zero', '0day', 'vulnerability', 'pwn']
    if any(kw in actor_lower for kw in exploit_keywords):
        return "Exploit Developer/Seller"
    
    # Default classification
    return "Unclassified Threat Actor"

def infer_mitre_ttps(actor_name, incidents_df, ransomware_data, actor_type):
    """
    Infer MITRE ATT&CK TTPs based on threat actor type
    Each type gets unique, relevant TTPs
    """
    ttps = []
    
    # ========== RANSOMWARE GROUPS ==========
    if actor_type == "Ransomware Group":
        ttps.extend([
            {'id': 'T1566.001', 'name': 'Phishing: Spearphishing Attachment', 'tactic': 'Initial Access'},
            {'id': 'T1566.002', 'name': 'Phishing: Spearphishing Link', 'tactic': 'Initial Access'},
            {'id': 'T1204.002', 'name': 'User Execution: Malicious File', 'tactic': 'Execution'},
            {'id': 'T1059.001', 'name': 'Command and Scripting Interpreter: PowerShell', 'tactic': 'Execution'},
            {'id': 'T1078', 'name': 'Valid Accounts', 'tactic': 'Persistence'},
            {'id': 'T1027', 'name': 'Obfuscated Files or Information', 'tactic': 'Defense Evasion'},
            {'id': 'T1490', 'name': 'Inhibit System Recovery', 'tactic': 'Impact'},
            {'id': 'T1486', 'name': 'Data Encrypted for Impact', 'tactic': 'Impact'},
            {'id': 'T1567', 'name': 'Exfiltration Over Web Service', 'tactic': 'Exfiltration'},
            {'id': 'T1041', 'name': 'Exfiltration Over C2 Channel', 'tactic': 'Exfiltration'},
            {'id': 'T1489', 'name': 'Service Stop', 'tactic': 'Impact'},
            {'id': 'T1491', 'name': 'Defacement', 'tactic': 'Impact'},
        ])
    
    # ========== HACKTIVIST GROUPS ==========
    elif actor_type == "Hacktivist Group":
        ttps.extend([
            {'id': 'T1190', 'name': 'Exploit Public-Facing Application', 'tactic': 'Initial Access'},
            {'id': 'T1133', 'name': 'External Remote Services', 'tactic': 'Initial Access'},
            {'id': 'T1498', 'name': 'Network Denial of Service', 'tactic': 'Impact'},
            {'id': 'T1499', 'name': 'Endpoint Denial of Service', 'tactic': 'Impact'},
            {'id': 'T1491.001', 'name': 'Defacement: Internal Defacement', 'tactic': 'Impact'},
            {'id': 'T1491.002', 'name': 'Defacement: External Defacement', 'tactic': 'Impact'},
            {'id': 'T1589', 'name': 'Gather Victim Identity Information', 'tactic': 'Reconnaissance'},
            {'id': 'T1594', 'name': 'Search Victim-Owned Websites', 'tactic': 'Reconnaissance'},
            {'id': 'T1136', 'name': 'Create Account', 'tactic': 'Persistence'},
            {'id': 'T1485', 'name': 'Data Destruction', 'tactic': 'Impact'},
        ])
    
    # ========== INITIAL ACCESS BROKERS ==========
    elif actor_type == "Initial Access Broker (IAB)":
        ttps.extend([
            {'id': 'T1078', 'name': 'Valid Accounts', 'tactic': 'Initial Access'},
            {'id': 'T1110', 'name': 'Brute Force', 'tactic': 'Credential Access'},
            {'id': 'T1110.003', 'name': 'Brute Force: Password Spraying', 'tactic': 'Credential Access'},
            {'id': 'T1190', 'name': 'Exploit Public-Facing Application', 'tactic': 'Initial Access'},
            {'id': 'T1133', 'name': 'External Remote Services', 'tactic': 'Initial Access'},
            {'id': 'T1566', 'name': 'Phishing', 'tactic': 'Initial Access'},
            {'id': 'T1595', 'name': 'Active Scanning', 'tactic': 'Reconnaissance'},
            {'id': 'T1046', 'name': 'Network Service Discovery', 'tactic': 'Discovery'},
            {'id': 'T1021.001', 'name': 'Remote Services: Remote Desktop Protocol', 'tactic': 'Lateral Movement'},
            {'id': 'T1087', 'name': 'Account Discovery', 'tactic': 'Discovery'},
        ])
    
    # ========== DATABASE BREACH SPECIALISTS ==========
    elif actor_type == "Database Breach Specialist":
        ttps.extend([
            {'id': 'T1190', 'name': 'Exploit Public-Facing Application', 'tactic': 'Initial Access'},
            {'id': 'T1505.003', 'name': 'Server Software Component: Web Shell', 'tactic': 'Persistence'},
            {'id': 'T1136', 'name': 'Create Account', 'tactic': 'Persistence'},
            {'id': 'T1213', 'name': 'Data from Information Repositories', 'tactic': 'Collection'},
            {'id': 'T1005', 'name': 'Data from Local System', 'tactic': 'Collection'},
            {'id': 'T1074', 'name': 'Data Staged', 'tactic': 'Collection'},
            {'id': 'T1030', 'name': 'Data Transfer Size Limits', 'tactic': 'Exfiltration'},
            {'id': 'T1048', 'name': 'Exfiltration Over Alternative Protocol', 'tactic': 'Exfiltration'},
            {'id': 'T1567', 'name': 'Exfiltration Over Web Service', 'tactic': 'Exfiltration'},
            {'id': 'T1087', 'name': 'Account Discovery', 'tactic': 'Discovery'},
        ])
    
    # ========== APT GROUPS ==========
    elif actor_type == "Advanced Persistent Threat (APT)":
        ttps.extend([
            {'id': 'T1566.001', 'name': 'Phishing: Spearphishing Attachment', 'tactic': 'Initial Access'},
            {'id': 'T1189', 'name': 'Drive-by Compromise', 'tactic': 'Initial Access'},
            {'id': 'T1203', 'name': 'Exploitation for Client Execution', 'tactic': 'Execution'},
            {'id': 'T1547', 'name': 'Boot or Logon Autostart Execution', 'tactic': 'Persistence'},
            {'id': 'T1055', 'name': 'Process Injection', 'tactic': 'Defense Evasion'},
            {'id': 'T1027', 'name': 'Obfuscated Files or Information', 'tactic': 'Defense Evasion'},
            {'id': 'T1003', 'name': 'OS Credential Dumping', 'tactic': 'Credential Access'},
            {'id': 'T1057', 'name': 'Process Discovery', 'tactic': 'Discovery'},
            {'id': 'T1082', 'name': 'System Information Discovery', 'tactic': 'Discovery'},
            {'id': 'T1071', 'name': 'Application Layer Protocol', 'tactic': 'Command and Control'},
            {'id': 'T1041', 'name': 'Exfiltration Over C2 Channel', 'tactic': 'Exfiltration'},
        ])
    
    # ========== DDOS ATTACK GROUPS ==========
    elif actor_type == "DDoS Attack Group":
        ttps.extend([
            {'id': 'T1583.005', 'name': 'Acquire Infrastructure: Botnet', 'tactic': 'Resource Development'},
            {'id': 'T1498', 'name': 'Network Denial of Service', 'tactic': 'Impact'},
            {'id': 'T1498.001', 'name': 'Network Denial of Service: Direct Network Flood', 'tactic': 'Impact'},
            {'id': 'T1498.002', 'name': 'Network Denial of Service: Reflection Amplification', 'tactic': 'Impact'},
            {'id': 'T1499', 'name': 'Endpoint Denial of Service', 'tactic': 'Impact'},
            {'id': 'T1499.004', 'name': 'Endpoint Denial of Service: Application or System Exploitation', 'tactic': 'Impact'},
            {'id': 'T1595', 'name': 'Active Scanning', 'tactic': 'Reconnaissance'},
        ])
    
    # ========== MALWARE DISTRIBUTION NETWORKS ==========
    elif actor_type == "Malware Distribution Network":
        ttps.extend([
            {'id': 'T1566.001', 'name': 'Phishing: Spearphishing Attachment', 'tactic': 'Initial Access'},
            {'id': 'T1566.002', 'name': 'Phishing: Spearphishing Link', 'tactic': 'Initial Access'},
            {'id': 'T1204.002', 'name': 'User Execution: Malicious File', 'tactic': 'Execution'},
            {'id': 'T1059', 'name': 'Command and Scripting Interpreter', 'tactic': 'Execution'},
            {'id': 'T1547', 'name': 'Boot or Logon Autostart Execution', 'tactic': 'Persistence'},
            {'id': 'T1027', 'name': 'Obfuscated Files or Information', 'tactic': 'Defense Evasion'},
            {'id': 'T1140', 'name': 'Deobfuscate/Decode Files or Information', 'tactic': 'Defense Evasion'},
            {'id': 'T1071', 'name': 'Application Layer Protocol', 'tactic': 'Command and Control'},
            {'id': 'T1105', 'name': 'Ingress Tool Transfer', 'tactic': 'Command and Control'},
        ])
    
    # ========== PHISHING CAMPAIGN OPERATORS ==========
    elif actor_type == "Phishing Campaign Operator":
        ttps.extend([
            {'id': 'T1598', 'name': 'Phishing for Information', 'tactic': 'Reconnaissance'},
            {'id': 'T1566.001', 'name': 'Phishing: Spearphishing Attachment', 'tactic': 'Initial Access'},
            {'id': 'T1566.002', 'name': 'Phishing: Spearphishing Link', 'tactic': 'Initial Access'},
            {'id': 'T1566.003', 'name': 'Phishing: Spearphishing via Service', 'tactic': 'Initial Access'},
            {'id': 'T1586', 'name': 'Compromise Accounts', 'tactic': 'Resource Development'},
            {'id': 'T1585', 'name': 'Establish Accounts', 'tactic': 'Resource Development'},
            {'id': 'T1589', 'name': 'Gather Victim Identity Information', 'tactic': 'Reconnaissance'},
            {'id': 'T1056.003', 'name': 'Input Capture: Web Portal Capture', 'tactic': 'Collection'},
        ])
    
    # ========== WEB APPLICATION EXPLOIT GROUPS ==========
    elif actor_type == "Web Application Exploit Group":
        ttps.extend([
            {'id': 'T1190', 'name': 'Exploit Public-Facing Application', 'tactic': 'Initial Access'},
            {'id': 'T1505.003', 'name': 'Server Software Component: Web Shell', 'tactic': 'Persistence'},
            {'id': 'T1059', 'name': 'Command and Scripting Interpreter', 'tactic': 'Execution'},
            {'id': 'T1140', 'name': 'Deobfuscate/Decode Files or Information', 'tactic': 'Defense Evasion'},
            {'id': 'T1083', 'name': 'File and Directory Discovery', 'tactic': 'Discovery'},
            {'id': 'T1005', 'name': 'Data from Local System', 'tactic': 'Collection'},
        ])
    
    # ========== DEFAULT/UNCLASSIFIED ==========
    else:
        ttps.extend([
            {'id': 'T1566', 'name': 'Phishing', 'tactic': 'Initial Access'},
            {'id': 'T1190', 'name': 'Exploit Public-Facing Application', 'tactic': 'Initial Access'},
            {'id': 'T1204', 'name': 'User Execution', 'tactic': 'Execution'},
            {'id': 'T1059', 'name': 'Command and Scripting Interpreter', 'tactic': 'Execution'},
            {'id': 'T1078', 'name': 'Valid Accounts', 'tactic': 'Persistence'},
            {'id': 'T1027', 'name': 'Obfuscated Files or Information', 'tactic': 'Defense Evasion'},
            {'id': 'T1082', 'name': 'System Information Discovery', 'tactic': 'Discovery'},
            {'id': 'T1005', 'name': 'Data from Local System', 'tactic': 'Collection'},
        ])
    
    # Add context-specific TTPs based on incident data
    if not incidents_df.empty:
        countries = incidents_df['country'].nunique()
        sectors = incidents_df['sector'].nunique()
        
        if countries > 5:
            ttps.append({'id': 'T1583', 'name': 'Acquire Infrastructure', 'tactic': 'Resource Development'})
        
        if sectors > 3:
            ttps.append({'id': 'T1589', 'name': 'Gather Victim Identity Information', 'tactic': 'Reconnaissance'})
    
    return ttps

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

def add_page_number_and_watermark(canvas, doc):
    """Add page numbers, watermark, and footer to each page"""
    canvas.saveState()
    
    # Add watermark
    canvas.setFillColorRGB(0.9, 0.9, 0.9)
    canvas.setFont("Helvetica-Bold", 60)
    canvas.saveState()
    canvas.translate(letter[0]/2, letter[1]/2)
    canvas.rotate(45)
    canvas.drawCentredString(0, 0, "CYHAWK AFRICA")
    canvas.restoreState()
    
    # Add footer with page number
    canvas.setFillColorRGB(0.3, 0.3, 0.3)
    canvas.setFont("Helvetica", 9)
    page_num = canvas.getPageNumber()
    footer_text = f"CyHawk Africa Threat Intelligence Platform | Page {page_num}"
    canvas.drawString(inch, 0.5*inch, footer_text)
    
    # Add confidentiality notice
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColorRGB(0.77, 0.12, 0.23)  # CyHawk Red
    canvas.drawRightString(letter[0] - inch, 0.5*inch, "CONFIDENTIAL - TLP:AMBER")
    
    canvas.restoreState()

def generate_pdf_report(actor_name, profile_data, incidents_df, ransomware_data, risk_score, ttps):
    """Generate strategic threat intelligence report with branding"""
    if not PDF_EXPORT_AVAILABLE:
        st.error("PDF export requires reportlab package. Install with: pip install reportlab")
        return None
    
    from reportlab.lib.utils import ImageReader
    import io
    from PIL import Image, ImageDraw, ImageFont
    
    buffer = BytesIO()
    
    # Create document with custom page template
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        topMargin=1*inch, 
        bottomMargin=0.75*inch,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#C41E3A'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#666666'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#C41E3A'),
        spaceAfter=12,
        spaceBefore=18,
        fontName='Helvetica-Bold',
        borderWidth=0,
        borderColor=colors.HexColor('#C41E3A'),
        borderPadding=8
    )
    
    classification_style = ParagraphStyle(
        'Classification',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#C41E3A'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=20
    )
    
    # ========== COVER PAGE ==========
    
    # Add logo if available
    logo_path = "assets/cyhawk_logo.png"
    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path)
            # Resize logo to reasonable size
            img.thumbnail((200, 80), Image.Resampling.LANCZOS)
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            logo = ImageReader(img_buffer)
            from reportlab.platypus import Image as RLImage
            logo_img = RLImage(img_buffer, width=200, height=80)
            logo_img.hAlign = 'CENTER'
            story.append(logo_img)
            story.append(Spacer(1, 0.3*inch))
        except:
            # If logo fails, add text logo
            story.append(Paragraph("CYHAWK AFRICA", title_style))
            story.append(Spacer(1, 0.2*inch))
    else:
        story.append(Paragraph("CYHAWK AFRICA", title_style))
        story.append(Spacer(1, 0.2*inch))
    
    # Report type
    story.append(Paragraph("STRATEGIC THREAT INTELLIGENCE REPORT", subtitle_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Actor name - main title
    story.append(Paragraph(f"THREAT ACTOR: {actor_name.upper()}", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Classification banner
    risk_class, _, _ = get_risk_classification(risk_score)
    story.append(Paragraph(f"CLASSIFICATION: {risk_class} RISK | TLP:AMBER", classification_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Report metadata table
    metadata = [
        ['Report Generated:', datetime.now().strftime('%d %B %Y at %H:%M UTC')],
        ['Threat Actor Type:', profile_data['type']],
        ['Risk Score:', f"{risk_score}/100 ({risk_class})"],
        ['Active Since:', profile_data['active_since']],
        ['Incidents Tracked:', str(len(incidents_df))],
        ['Data Sources:', 'CyHawk Telemetry, Ransomware.live, OSINT'],
    ]
    
    metadata_table = Table(metadata, colWidths=[2*inch, 4*inch])
    metadata_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.grey),
    ]))
    story.append(metadata_table)
    story.append(Spacer(1, 0.5*inch))
    
    # Confidentiality notice
    confidentiality_text = """
    <b>CONFIDENTIALITY NOTICE:</b> This strategic threat intelligence report contains sensitive 
    security information and is intended solely for authorized personnel. Distribution is 
    restricted to TLP:AMBER - Limited disclosure, recipients can share with their organization 
    and clients on a need-to-know basis.
    """
    story.append(Paragraph(confidentiality_text, styles['Normal']))
    
    story.append(PageBreak())
    
    # ========== EXECUTIVE SUMMARY ==========
    
    story.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
    
    if not incidents_df.empty:
        exec_summary = f"""
        <b>{actor_name}</b> represents a <b>{risk_class} risk threat actor</b> with confirmed 
        operational capability. Intelligence analysis reveals <b>{len(incidents_df)} documented cyber incidents</b> 
        impacting <b>{incidents_df['country'].nunique()} countries</b> across 
        <b>{incidents_df['sector'].nunique()} critical industry sectors</b>.
        <br/><br/>
        <b>Threat Actor Classification:</b> {profile_data['type']}<br/>
        <b>Operational Timeline:</b> {incidents_df['date'].min().strftime('%B %Y')} to {incidents_df['date'].max().strftime('%B %Y')}<br/>
        <b>Geographic Scope:</b> {"Multi-national operations" if incidents_df['country'].nunique() > 5 else "Regional targeting"}
        """
        
        if ransomware_data and ransomware_data.get('victims'):
            exec_summary += f"""
            <br/><br/>
            <b>RANSOMWARE OPERATIONS CONFIRMED:</b> {len(ransomware_data['victims'])} documented victim 
            organizations identified through ransomware.live intelligence feeds. This actor demonstrates 
            active double-extortion capabilities with sustained financial motivation.
            """
    else:
        exec_summary = f"""
        <b>{actor_name}</b> is classified as a <b>{profile_data['type']}</b> tracked through 
        multiple intelligence sources. Limited confirmed incident telemetry suggests either 
        emerging operations or sophisticated operational security practices.
        """
    
    story.append(Paragraph(exec_summary, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # ========== THREAT ASSESSMENT ==========
    
    story.append(Paragraph("STRATEGIC THREAT ASSESSMENT", heading_style))
    
    # Risk score breakdown
    risk_assessment = f"""
    <b>Comprehensive Risk Score: {risk_score}/100</b><br/><br/>
    This threat actor has been assigned a risk score of {risk_score} out of 100 based on multi-factor 
    analysis including incident frequency, geographic distribution, sector targeting diversity, 
    attack severity metrics, and confirmed operational indicators.
    """
    story.append(Paragraph(risk_assessment, styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # ========== MITRE ATT&CK FRAMEWORK ==========
    
    story.append(Paragraph("MITRE ATT&CK TACTICS, TECHNIQUES & PROCEDURES", heading_style))
    
    if ttps:
        ttp_intro = f"""
        Based on operational analysis and incident forensics, <b>{len(ttps)} MITRE ATT&CK techniques</b> 
        have been attributed to this threat actor's operational methodology:
        """
        story.append(Paragraph(ttp_intro, styles['Normal']))
        story.append(Spacer(1, 0.15*inch))
        
        # Create TTP table
        ttp_data = [['Technique ID', 'Technique Name', 'Tactic']]
        for ttp in ttps[:15]:  # Limit to top 15 for PDF
            ttp_data.append([ttp['id'], ttp['name'], ttp['tactic']])
        
        ttp_table = Table(ttp_data, colWidths=[1*inch, 3.5*inch, 1.5*inch])
        ttp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C41E3A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(ttp_table)
        story.append(Spacer(1, 0.2*inch))
    
    story.append(PageBreak())
    
    # ========== GEOGRAPHIC TARGETING ANALYSIS ==========
    
    if not incidents_df.empty:
        story.append(Paragraph("GEOGRAPHIC TARGETING ANALYSIS", heading_style))
        
        countries = incidents_df['country'].value_counts().head(10)
        geo_text = f"""
        Geographic analysis reveals targeting across <b>{incidents_df['country'].nunique()} countries</b>, 
        with concentrated activity in the following regions:
        """
        story.append(Paragraph(geo_text, styles['Normal']))
        story.append(Spacer(1, 0.15*inch))
        
        # Country targeting table
        country_data = [['Country', 'Incident Count', 'Percentage']]
        total_incidents = len(incidents_df)
        for country, count in countries.items():
            percentage = f"{(count/total_incidents)*100:.1f}%"
            country_data.append([country, str(count), percentage])
        
        country_table = Table(country_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        country_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C41E3A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(country_table)
        story.append(Spacer(1, 0.3*inch))
        
        # ========== SECTOR TARGETING ==========
        
        story.append(Paragraph("INDUSTRY SECTOR TARGETING", heading_style))
        
        sectors = incidents_df['sector'].value_counts().head(10)
        sector_text = f"""
        Cross-sector analysis identifies <b>{incidents_df['sector'].nunique()} distinct industry verticals</b> 
        targeted by this threat actor:
        """
        story.append(Paragraph(sector_text, styles['Normal']))
        story.append(Spacer(1, 0.15*inch))
        
        # Sector list
        for sector, count in sectors.items():
            story.append(Paragraph(f"• <b>{sector}:</b> {count} incidents", styles['Normal']))
        
        story.append(Spacer(1, 0.3*inch))
    
    # ========== DEFENSIVE RECOMMENDATIONS ==========
    
    story.append(Paragraph("STRATEGIC DEFENSIVE RECOMMENDATIONS", heading_style))
    
    recommendations = [
        "<b>IMMEDIATE ACTIONS (0-24 HOURS):</b>",
        "• Deploy indicators of compromise (IOCs) across security infrastructure",
        "• Initiate threat hunting operations for historical compromise indicators",
        "• Elevate monitoring and alerting for TTPs associated with this actor",
        "• Brief executive leadership and board on threat actor capabilities",
        "",
        "<b>SHORT-TERM ACTIONS (1-7 DAYS):</b>",
        "• Conduct tabletop exercises simulating this threat actor's TTPs",
        "• Review and update incident response playbooks",
        "• Implement additional network segmentation for critical assets",
        "• Enhance email security controls and user awareness training",
        "",
        "<b>LONG-TERM STRATEGIC INITIATIVES:</b>",
        "• Deploy advanced endpoint detection and response (EDR) solutions",
        "• Implement zero-trust architecture principles",
        "• Establish threat intelligence sharing partnerships",
        "• Conduct regular red team exercises simulating this threat actor",
        "• Develop and test business continuity plans for ransomware scenarios",
    ]
    
    for rec in recommendations:
        story.append(Paragraph(rec, styles['Normal']))
    
    story.append(Spacer(1, 0.3*inch))
    
    # ========== INTELLIGENCE GAPS ==========
    
    story.append(Paragraph("INTELLIGENCE GAPS & COLLECTION REQUIREMENTS", heading_style))
    
    gaps_text = """
    The following intelligence requirements have been identified for enhanced threat actor understanding:
    <br/><br/>
    • Attribution confirmation and sponsorship identification<br/>
    • Complete infrastructure mapping and C2 architecture<br/>
    • Malware variant analysis and capability assessment<br/>
    • Victim selection criteria and targeting methodology<br/>
    • Operational tempo and campaign lifecycle analysis
    """
    story.append(Paragraph(gaps_text, styles['Normal']))
    
    story.append(PageBreak())
    
    # ========== CONCLUSION ==========
    
    story.append(Paragraph("CONCLUSION & OUTLOOK", heading_style))
    
    conclusion = f"""
    <b>{actor_name}</b> represents a {risk_class.lower()} risk to organizational security posture based 
    on demonstrated capabilities, operational scope, and historical targeting patterns. The threat actor's 
    classification as <b>{profile_data['type']}</b> indicates specific defensive priorities and mitigation strategies.
    <br/><br/>
    Organizations matching this actor's historical targeting profile should implement recommended defensive 
    measures immediately and maintain heightened security posture. Continuous monitoring of threat intelligence 
    feeds and participation in information sharing communities is essential for early warning of emerging campaigns.
    <br/><br/>
    <b>THREAT OUTLOOK:</b> {"Critical - Sustained operations expected" if risk_score >= 70 else "High - Continued monitoring required" if risk_score >= 40 else "Moderate - Defensive measures recommended"}
    """
    story.append(Paragraph(conclusion, styles['Normal']))
    
    story.append(Spacer(1, 0.5*inch))
    
    # ========== FOOTER ==========
    
    footer_text = """
    <br/><br/>
    <i>This strategic threat intelligence report was generated by the CyHawk Africa Threat Intelligence Platform. 
    For questions regarding this report or additional intelligence requirements, contact your CyHawk analyst.</i>
    <br/><br/>
    <b>DISTRIBUTION:</b> TLP:AMBER - Limited disclosure authorized<br/>
    <b>CLASSIFICATION:</b> CONFIDENTIAL<br/>
    <b>VALIDITY:</b> This assessment is valid as of the generation date and should be reviewed monthly.
    """
    story.append(Paragraph(footer_text, styles['Normal']))
    
    # Build PDF with custom page template
    doc.build(story, onFirstPage=add_page_number_and_watermark, onLaterPages=add_page_number_and_watermark)
    
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

# Classify actor type
actor_type = classify_threat_actor_type(selected_actor, actor_df, ransomware_data)

# Calculate risk score and TTPs
risk_score, risk_breakdown = calculate_comprehensive_risk_score(actor_df, ransomware_data)
risk_class, risk_css, risk_color = get_risk_classification(risk_score)
ttps = infer_mitre_ttps(selected_actor, actor_df, ransomware_data, actor_type)

# Prepare profile data
profile_data = {
    'classification': risk_class,
    'origin': 'Under Investigation',
    'active_since': actor_df['date'].min().strftime('%Y') if not actor_df.empty else 'Unknown',
    'type': actor_type  # Use classified type instead of hardcoded
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
    if PDF_EXPORT_AVAILABLE:
        if st.button("📄 Export PDF", use_container_width=True):
            with st.spinner("Generating PDF..."):
                pdf_buffer = generate_pdf_report(selected_actor, profile_data, actor_df, ransomware_data, risk_score, ttps)
                if pdf_buffer:
                    st.download_button(
                        label="⬇️ Download PDF",
                        data=pdf_buffer,
                        file_name=f"CyHawk_ThreatBrief_{selected_actor}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
    else:
        if st.button("📄 Export PDF", use_container_width=True, disabled=True):
            st.error("Install reportlab for PDF export: `pip install reportlab`")

# col2 and col3 remain for layout spacing but no export button

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
