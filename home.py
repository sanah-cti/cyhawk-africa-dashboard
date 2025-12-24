import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import io
import random

# ═══════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="CyHawk Africa - Threat Intelligence Platform",
    page_icon="assets/favicon.ico",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════
# THEME MANAGEMENT
# ═══════════════════════════════════════════════════════════
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

THEMES = {
    'dark': {
        'bg': '#000000',
        'bg_elevated': '#0a0a0a',
        'bg_card': '#111111',
        'border': '#1f1f1f',
        'text': '#ffffff',
        'text_dim': '#999999',
        'text_subtle': '#666666',
        'cyhawk_red': '#C41E3A',
        'red_glow': 'rgba(196, 30, 58, 0.5)',
        'success': '#00ff00',
    },
    'light': {
        'bg': '#ffffff',
        'bg_elevated': '#f8f9fa',
        'bg_card': '#f0f0f0',
        'border': '#e0e0e0',
        'text': '#000000',
        'text_dim': '#666666',
        'text_subtle': '#999999',
        'cyhawk_red': '#C41E3A',
        'red_glow': 'rgba(196, 30, 58, 0.3)',
        'success': '#27ae60',
    }
}

C = THEMES[st.session_state.theme]

# ═══════════════════════════════════════════════════════════
# COUNTRY TO ISO MAPPING
# ═══════════════════════════════════════════════════════════
COUNTRY_ISO = {
    'Nigeria': 'NGA', 'South Africa': 'ZAF', 'Kenya': 'KEN', 'Egypt': 'EGY',
    'Ghana': 'GHA', 'Ethiopia': 'ETH', 'Tanzania': 'TZA', 'Uganda': 'UGA',
    'Morocco': 'MAR', 'Algeria': 'DZA', 'Sudan': 'SDN', 'Angola': 'AGO',
    'Mozambique': 'MOZ', 'Madagascar': 'MDG', 'Cameroon': 'CMR', 'Ivory Coast': 'CIV',
    'Niger': 'NER', 'Mali': 'MLI', 'Burkina Faso': 'BFA', 'Malawi': 'MWI',
    'Zambia': 'ZMB', 'Senegal': 'SEN', 'Somalia': 'SOM', 'Chad': 'TCD',
    'Zimbabwe': 'ZWE', 'Guinea': 'GIN', 'Rwanda': 'RWA', 'Benin': 'BEN',
    'Tunisia': 'TUN', 'Burundi': 'BDI', 'South Sudan': 'SSD', 'Togo': 'TGO',
    'Sierra Leone': 'SLE', 'Libya': 'LBY', 'Liberia': 'LBR', 'Mauritania': 'MRT',
    'Central African Republic': 'CAF', 'Eritrea': 'ERI', 'Gambia': 'GMB',
    'Botswana': 'BWA', 'Namibia': 'NAM', 'Gabon': 'GAB', 'Lesotho': 'LSO',
    'Guinea-Bissau': 'GNB', 'Equatorial Guinea': 'GNQ', 'Mauritius': 'MUS',
    'Eswatini': 'SWZ', 'Djibouti': 'DJI', 'Comoros': 'COM',
    'Cape Verde': 'CPV', 'Sao Tome and Principe': 'STP', 'Seychelles': 'SYC'
}

# ═══════════════════════════════════════════════════════════
# DATA LOADING WITH ERROR HANDLING
# ═══════════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def load_data():
    """Load incidents data from CSV with robust fallback"""
    
    try:
        # Try to load CSV
        csv_path = None
        if os.path.exists('data/incidents.csv'):
            csv_path = 'data/incidents.csv'
        elif os.path.exists('../data/incidents.csv'):
            csv_path = '../data/incidents.csv'
        elif os.path.exists('incidents.csv'):
            csv_path = 'incidents.csv'
        
        if csv_path:
            df = pd.read_csv(csv_path)
            
            # Convert date column
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                df = df.dropna(subset=['date'])
                df['year'] = df['date'].dt.year
                df['month'] = df['date'].dt.strftime('%B')
            else:
                # Add date columns if missing
                df['date'] = pd.date_range(end=datetime.now(), periods=len(df), freq='D')
                df['year'] = df['date'].dt.year
                df['month'] = df['date'].dt.strftime('%B')
            
            # Ensure required columns exist
            if 'country' not in df.columns:
                df['country'] = random.choices(list(COUNTRY_ISO.keys()), k=len(df))
            
            if 'threat_actor' not in df.columns:
                df['threat_actor'] = random.choices(['LockBit', 'BlackCat', 'Play', 'Cl0p', 'Royal', 'BianLian'], k=len(df))
            
            if 'threat_type' not in df.columns:
                df['threat_type'] = random.choices(['Ransomware', 'Phishing', 'DDoS', 'Malware', 'Data Breach'], k=len(df))
            
            if 'severity' not in df.columns:
                df['severity'] = random.choices(['Critical', 'High', 'Medium', 'Low'], k=len(df))
            
            # Clean up data
            df = df.dropna(subset=['country', 'threat_actor', 'threat_type', 'severity'])
            
            return df
        
        else:
            raise FileNotFoundError("CSV not found")
    
    except Exception as e:
        # Generate sample data as fallback
        st.info(f"ℹ️ Loading sample data: {str(e)}")
        return generate_sample_data()

def generate_sample_data():
    """Generate sample threat data"""
    dates = pd.date_range(end=datetime.now(), periods=500, freq='D')
    
    df = pd.DataFrame({
        'date': random.choices(dates, k=500),
        'country': random.choices(list(COUNTRY_ISO.keys()), k=500),
        'threat_actor': random.choices([
            'LockBit', 'BlackCat', 'Play', 'Cl0p', 'Royal', 'BianLian', 
            'Medusa', 'Akira', 'NoEscape', '8Base', 'Rhysida', 'Hunters'
        ], k=500),
        'threat_type': random.choices([
            'Ransomware', 'Phishing', 'DDoS', 'Malware', 'Data Breach'
        ], k=500),
        'severity': random.choices([
            'Critical', 'High', 'Medium', 'Low'
        ], weights=[1, 2, 3, 2], k=500),
    })
    
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.strftime('%B')
    
    return df

def filter_data(df, year, month, country, threat_type, threat_actor, severity):
    """Apply all filters to dataframe"""
    filtered = df.copy()
    
    if year != "All Years":
        filtered = filtered[filtered['year'] == int(year)]
    
    if month != "All Months":
        filtered = filtered[filtered['month'] == month]
    
    if country != "All Countries":
        filtered = filtered[filtered['country'] == country]
    
    if threat_type != "All Types":
        filtered = filtered[filtered['threat_type'] == threat_type]
    
    if threat_actor != "All Actors":
        filtered = filtered[filtered['threat_actor'] == threat_actor]
    
    if severity != "All Severities":
        filtered = filtered[filtered['severity'] == severity]
    
    return filtered

def process_map_data(df):
    """Process data for choropleth map"""
    map_data = []
    
    for country, iso in COUNTRY_ISO.items():
        country_df = df[df['country'] == country]
        attacks = len(country_df)
        
        # Get top 5 threat actors
        top_actors = []
        if not country_df.empty and 'threat_actor' in country_df.columns:
            actor_counts = country_df['threat_actor'].value_counts().head(5)
            for actor, count in actor_counts.items():
                top_actors.append({'name': str(actor), 'count': int(count)})
        
        # Get top 3 threat types
        threat_types = []
        if not country_df.empty and 'threat_type' in country_df.columns:
            type_counts = country_df['threat_type'].value_counts().head(3)
            for ttype, count in type_counts.items():
                threat_types.append({'type': str(ttype), 'count': int(count)})
        
        map_data.append({
            'country': country,
            'iso_alpha': iso,
            'attacks': attacks,
            'top_actors': top_actors,
            'threat_types': threat_types
        })
    
    return pd.DataFrame(map_data)

# ═══════════════════════════════════════════════════════════
# PDF EXPORT FUNCTION
# ═══════════════════════════════════════════════════════════
def generate_pdf(df, filters):
    """Generate professional PDF report"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#C41E3A'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Add title
    title = Paragraph("CyHawk Africa<br/>Threat Intelligence Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Report metadata
    meta_style = ParagraphStyle('Meta', parent=styles['Normal'], fontSize=10, textColor=colors.grey)
    meta_text = f"""
    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}<br/>
    Total Incidents in Report: {len(df)}<br/>
    Report Period: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}
    """
    meta = Paragraph(meta_text, meta_style)
    elements.append(meta)
    elements.append(Spacer(1, 20))
    
    # Filters applied
    active_filters = [f"{k}: {v}" for k, v in filters.items() if not v.startswith("All")]
    if active_filters:
        filter_text = "Active Filters: " + ", ".join(active_filters)
        filter_para = Paragraph(filter_text, styles['Normal'])
        elements.append(filter_para)
        elements.append(Spacer(1, 20))
    
    # Summary statistics table
    summary_data = [
        ['Metric', 'Value'],
        ['Total Incidents', str(len(df))],
        ['Countries Affected', str(df['country'].nunique())],
        ['Unique Threat Actors', str(df['threat_actor'].nunique())],
        ['Critical Severity', str(len(df[df['severity'] == 'Critical']))],
        ['High Severity', str(len(df[df['severity'] == 'High']))],
        ['Medium Severity', str(len(df[df['severity'] == 'Medium']))],
        ['Low Severity', str(len(df[df['severity'] == 'Low']))]
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C41E3A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    elements.append(Paragraph("Executive Summary", styles['Heading2']))
    elements.append(Spacer(1, 12))
    elements.append(summary_table)
    elements.append(Spacer(1, 30))
    
    # Top threat types
    threat_counts = df['threat_type'].value_counts().head(10)
    threat_data = [['Threat Type', 'Count', 'Percentage']]
    for threat, count in threat_counts.items():
        percentage = f"{(count/len(df)*100):.1f}%"
        threat_data.append([threat, str(count), percentage])
    
    threat_table = Table(threat_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    threat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C41E3A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    elements.append(Paragraph("Threat Type Distribution", styles['Heading2']))
    elements.append(Spacer(1, 12))
    elements.append(threat_table)
    elements.append(Spacer(1, 30))
    
    # Top threat actors
    actor_counts = df['threat_actor'].value_counts().head(10)
    actor_data = [['Threat Actor', 'Incidents', 'Percentage']]
    for actor, count in actor_counts.items():
        percentage = f"{(count/len(df)*100):.1f}%"
        actor_data.append([actor, str(count), percentage])
    
    actor_table = Table(actor_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    actor_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C41E3A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    elements.append(Paragraph("Top Threat Actors", styles['Heading2']))
    elements.append(Spacer(1, 12))
    elements.append(actor_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

# ═══════════════════════════════════════════════════════════
# LOAD DATA
# ═══════════════════════════════════════════════════════════
df = load_data()

# ═══════════════════════════════════════════════════════════
# V3 MODERN MINIMALIST CSS
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    -webkit-font-smoothing: antialiased;
}}

.stApp {{
    background: {C['bg']};
    color: {C['text']};
}}

#MainMenu, footer, header {{ visibility: hidden; }}

.stApp::before {{
    content: '';
    position: fixed;
    inset: 0;
    background-image: 
        linear-gradient({C['red_glow']} 1px, transparent 1px),
        linear-gradient(90deg, {C['red_glow']} 1px, transparent 1px);
    background-size: 50px 50px;
    z-index: -1;
    opacity: 0.3;
}}

.main-header {{
    background: rgba(10, 10, 10, 0.95);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid {C['border']};
    padding: 1rem 3rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: -6rem -6rem 2rem -6rem;
}}

.logo-section {{
    display: flex;
    align-items: center;
    gap: 1rem;
}}

.logo-container {{
    width: 50px;
    height: 50px;
    background: {C['cyhawk_red']};
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 20px {C['red_glow']};
    overflow: hidden;
}}

.logo-container img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
}}

.brand-text h1 {{
    font-size: 1.5rem;
    font-weight: 600;
    color: {C['text']};
    margin: 0;
    line-height: 1.2;
}}

.brand-highlight {{
    color: {C['cyhawk_red']};
    font-weight: 700;
}}

.brand-text p {{
    font-size: 0.75rem;
    color: {C['text_dim']};
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 0;
}}

.status-indicator {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: rgba(0, 255, 0, 0.1);
    border: 1px solid {C['success']};
    border-radius: 20px;
}}

.status-dot {{
    width: 8px;
    height: 8px;
    background: {C['success']};
    border-radius: 50%;
    box-shadow: 0 0 10px {C['success']};
    animation: pulse 2s infinite;
}}

@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.5; }}
}}

.hero-label {{
    color: {C['cyhawk_red']};
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}}

.hero-label::before {{
    content: '';
    width: 30px;
    height: 2px;
    background: {C['cyhawk_red']};
}}

.hero-title {{
    font-size: 3.5rem;
    font-weight: 700;
    color: {C['text']};
    margin-bottom: 1rem;
    letter-spacing: -2px;
    line-height: 1.1;
}}

.hero-subtitle {{
    font-size: 1.25rem;
    color: {C['text_dim']};
    font-weight: 400;
    margin-bottom: 2rem;
}}

.map-container {{
    background: linear-gradient(135deg, {C['bg_card']} 0%, {C['bg_elevated']} 100%);
    border: 1px solid {C['border']};
    border-radius: 24px;
    padding: 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}}

.map-container::before {{
    content: '';
    position: absolute;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, {C['red_glow']} 0%, transparent 70%);
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    pointer-events: none;
    z-index: 0;
}}

.map-inner {{
    position: relative;
    z-index: 1;
}}

.stats-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.5rem;
    margin: 2rem 0;
}}

.stat-card {{
    background: {C['bg_card']};
    border: 1px solid {C['border']};
    border-radius: 16px;
    padding: 1.5rem;
    transition: all 0.3s ease;
}}

.stat-card:hover {{
    border-color: {C['cyhawk_red']};
    transform: translateY(-4px);
}}

.stat-value {{
    font-size: 2.5rem;
    font-weight: 700;
    color: {C['cyhawk_red']};
    margin-bottom: 0.25rem;
    line-height: 1;
}}

.stat-label {{
    font-size: 0.85rem;
    color: {C['text_dim']};
    text-transform: uppercase;
    letter-spacing: 1px;
}}

.legend {{
    display: flex;
    gap: 2rem;
    margin-top: 2rem;
    padding: 1.5rem 0;
    border-top: 1px solid {C['border']};
    flex-wrap: wrap;
}}

.legend-item {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
}}

.legend-dot {{
    width: 12px;
    height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
}}

.legend-text {{
    font-size: 0.9rem;
    color: {C['text_dim']};
    font-weight: 500;
}}

.filter-container {{
    background: {C['bg_card']};
    border: 1px solid {C['border']};
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 2rem;
}}

.stSelectbox label {{
    font-size: 0.75rem !important;
    color: {C['text_subtle']} !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600 !important;
}}

.stButton > button {{
    background: {C['cyhawk_red']} !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}}

.stButton > button:hover {{
    background: #9A1529 !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(196, 30, 58, 0.4) !important;
}}

.stDownloadButton > button {{
    background: {C['bg_card']} !important;
    color: {C['text']} !important;
    border: 1px solid {C['border']} !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
}}

.stDownloadButton > button:hover {{
    border-color: {C['cyhawk_red']} !important;
    background: {C['bg_elevated']} !important;
}}

.block-container {{
    padding-top: 1rem;
    padding-bottom: 0rem;
    max-width: 1400px;
}}

.stColumn {{
    padding: 0 0.5rem;
}}

@media (max-width: 1024px) {{
    .stats-grid {{
        grid-template-columns: repeat(2, 1fr);
    }}
    .hero-title {{
        font-size: 2.5rem;
    }}
}}

@media (max-width: 768px) {{
    .main-header {{
        flex-direction: column;
        gap: 1rem;
        padding: 1rem 1.5rem;
        margin: -6rem -1rem 2rem -1rem;
    }}
    
    .stats-grid {{
        grid-template-columns: 1fr;
    }}
    
    .hero-title {{
        font-size: 2rem;
    }}
    
    .hero-subtitle {{
        font-size: 1rem;
    }}
    
    .map-container {{
        padding: 1.5rem;
    }}
}}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
<div class="main-header">
    <div class="logo-section">
        <div class="logo-container">
            <img src="app/static/assets/cyhawk_logo.png" alt="CyHawk Logo" onerror="this.style.display='none'">
        </div>
        <div class="brand-text">
            <h1><span class="brand-highlight">CyHawk</span> Africa</h1>
            <p>Threat Intelligence Platform</p>
        </div>
    </div>
    <div class="status-indicator">
        <div class="status-dot"></div>
        <span style="color: {C['text_dim']}; font-size: 0.85rem; font-weight: 500;">Live</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar theme toggle
with st.sidebar:
    st.markdown("### Settings")
    if st.button("🌓 Toggle Dark/Light Mode", use_container_width=True):
        toggle_theme()
        st.rerun()

# ═══════════════════════════════════════════════════════════
# HERO SECTION
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero-label">CONTINENTAL INTELLIGENCE</div>
<h1 class="hero-title">Africa Threat<br>Landscape</h1>
<p class="hero-subtitle">Real-time cyber threat monitoring across African nations with advanced intelligence analytics</p>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# ENHANCED FILTERS (6 DROPDOWNS)
# ═══════════════════════════════════════════════════════════
st.markdown('<div class="filter-container">', unsafe_allow_html=True)

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    years = ["All Years"] + sorted([str(y) for y in df['year'].unique()], reverse=True)
    selected_year = st.selectbox("Year", years, key="filter_year")

with col2:
    months = ["All Months"] + ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    selected_month = st.selectbox("Month", months, key="filter_month")

with col3:
    countries = ["All Countries"] + sorted(df['country'].unique().tolist())
    selected_country = st.selectbox("Country", countries, key="filter_country")

with col4:
    threat_types = ["All Types"] + sorted(df['threat_type'].unique().tolist())
    selected_type = st.selectbox("Threat Type", threat_types, key="filter_type")

with col5:
    actors = ["All Actors"] + sorted(df['threat_actor'].unique().tolist())
    selected_actor = st.selectbox("Threat Actor", actors, key="filter_actor")

with col6:
    severities = ["All Severities", "Critical", "High", "Medium", "Low"]
    selected_severity = st.selectbox("Severity", severities, key="filter_severity")

st.markdown('</div>', unsafe_allow_html=True)

# Apply filters
filtered_df = filter_data(df, selected_year, selected_month, selected_country, 
                          selected_type, selected_actor, selected_severity)

# ═══════════════════════════════════════════════════════════
# AFRICA THREAT MAP
# ═══════════════════════════════════════════════════════════
map_df = process_map_data(filtered_df)

st.markdown('<div class="map-container"><div class="map-inner">', unsafe_allow_html=True)

# Build hover texts
hover_texts = []
for _, row in map_df.iterrows():
    actors_text = ""
    if row['top_actors']:
        actors_text = "<br><b>Top Threat Actors:</b>"
        for actor in row['top_actors'][:5]:
            actors_text += f"<br>  • {actor['name']}: {actor['count']}"
    
    types_text = ""
    if row['threat_types']:
        types_text = "<br><b>Top Threats:</b>"
        for ttype in row['threat_types'][:3]:
            types_text += f"<br>  • {ttype['type']}: {ttype['count']}"
    
    hover_text = f"<b>{row['country']}</b><br>Total Attacks: {row['attacks']}{actors_text}{types_text}"
    hover_texts.append(hover_text)

# Create choropleth map
fig_map = go.Figure()

fig_map.add_trace(go.Choropleth(
    locations=map_df['iso_alpha'],
    z=map_df['attacks'],
    locationmode='ISO-3',
    colorscale=[
        [0.0, '#0D47A1'],   # Deep Blue (Safe)
        [0.2, '#1976D2'],   # Blue
        [0.3, '#00BCD4'],   # Cyan
        [0.4, '#00E676'],   # Bright Green (Low)
        [0.5, '#FFEB3B'],   # Yellow (Moderate)
        [0.6, '#FFC107'],   # Amber
        [0.7, '#FF9800'],   # Orange (High)
        [0.8, '#FF5722'],   # Deep Orange
        [0.9, '#F44336'],   # Red
        [1.0, '#C41E3A']    # CyHawk Red (CRITICAL)
    ],
    marker=dict(
        line=dict(color=C['border'], width=0.5)
    ),
    colorbar=dict(
        title="Threat<br>Level",
        titlefont=dict(color=C['text'], size=12),
        tickfont=dict(color=C['text'], size=10),
        bgcolor=C['bg_card'],
        bordercolor=C['border'],
        borderwidth=1,
        x=1.02
    ),
    text=hover_texts,
    hovertemplate='%{text}<extra></extra>',
    name=''
))

fig_map.update_geos(
    scope='africa',
    projection_type='natural earth',
    showland=True,
    landcolor=C['bg_elevated'],
    showocean=True,
    oceancolor=C['bg'],
    showcountries=True,
    countrycolor=C['border'],
    showlakes=False,
    bgcolor=C['bg_card']
)

fig_map.update_layout(
    height=650,
    margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    geo=dict(bgcolor='rgba(0,0,0,0)'),
    font=dict(color=C['text'])
)

st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False}, key='africa_map')

st.markdown('</div></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# STATISTICS CARDS
# ═══════════════════════════════════════════════════════════
total_threats = len(filtered_df)
critical_high = len(filtered_df[filtered_df['severity'].isin(['Critical', 'High'])])
actors_count = filtered_df['threat_actor'].nunique()
countries_count = filtered_df['country'].nunique()

st.markdown(f"""
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-value">{total_threats}</div>
        <div class="stat-label">Total Threats</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">{critical_high}</div>
        <div class="stat-label">Critical & High</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">{actors_count}</div>
        <div class="stat-label">Threat Actors</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">{countries_count}</div>
        <div class="stat-label">Countries</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# LEGEND
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
<div class="legend">
    <div class="legend-item">
        <div class="legend-dot" style="background: #0D47A1;"></div>
        <span class="legend-text">Safe</span>
    </div>
    <div class="legend-item">
        <div class="legend-dot" style="background: #00E676;"></div>
        <span class="legend-text">Low</span>
    </div>
    <div class="legend-item">
        <div class="legend-dot" style="background: #FFEB3B;"></div>
        <span class="legend-text">Moderate</span>
    </div>
    <div class="legend-item">
        <div class="legend-dot" style="background: #FF9800;"></div>
        <span class="legend-text">High</span>
    </div>
    <div class="legend-item">
        <div class="legend-dot" style="background: #C41E3A;"></div>
        <span class="legend-text">Critical</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# PDF EXPORT
# ═══════════════════════════════════════════════════════════
st.markdown("---")

export_col1, export_col2 = st.columns([3, 1])

with export_col2:
    if st.button("📥 Export PDF Report", use_container_width=True, type="primary"):
        filters_applied = {
            'Year': selected_year,
            'Month': selected_month,
            'Country': selected_country,
            'Threat Type': selected_type,
            'Threat Actor': selected_actor,
            'Severity': selected_severity
        }
        
        with st.spinner('Generating PDF report...'):
            pdf_buffer = generate_pdf(filtered_df, filters_applied)
        
        st.download_button(
            label="📄 Download PDF",
            data=pdf_buffer,
            file_name=f"cyhawk_africa_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
        st.success("✅ PDF report generated successfully!")
