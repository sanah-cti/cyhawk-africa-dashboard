import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
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
# DATA LOADING
# ═══════════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def load_data():
    """Load incidents data from CSV with robust fallback"""
    
    try:
        csv_path = None
        if os.path.exists('data/incidents.csv'):
            csv_path = 'data/incidents.csv'
        elif os.path.exists('../data/incidents.csv'):
            csv_path = '../data/incidents.csv'
        elif os.path.exists('incidents.csv'):
            csv_path = 'incidents.csv'
        
        if csv_path:
            df = pd.read_csv(csv_path)
            
            # Process dates
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                df = df.dropna(subset=['date'])
            else:
                df['date'] = pd.date_range(end=datetime.now(), periods=len(df), freq='D')
            
            df['year'] = df['date'].dt.year
            df['month'] = df['date'].dt.strftime('%B')
            
            # Ensure required columns
            if 'country' not in df.columns:
                df['country'] = random.choices(list(COUNTRY_ISO.keys()), k=len(df))
            if 'threat_actor' not in df.columns:
                df['threat_actor'] = random.choices(['LockBit', 'BlackCat', 'Play', 'Cl0p', 'Royal'], k=len(df))
            if 'threat_type' not in df.columns:
                df['threat_type'] = random.choices(['Ransomware', 'Phishing', 'DDoS', 'Malware'], k=len(df))
            if 'severity' not in df.columns:
                df['severity'] = random.choices(['Critical', 'High', 'Medium', 'Low'], k=len(df))
            if 'industry' not in df.columns:
                df['industry'] = random.choices(['Financial', 'Healthcare', 'Government', 'Energy'], k=len(df))
            
            df = df.dropna(subset=['country', 'threat_actor', 'threat_type', 'severity'])
            return df
        else:
            raise FileNotFoundError("CSV not found")
    
    except:
        return generate_sample_data()

def generate_sample_data():
    """Generate comprehensive sample data"""
    dates = pd.date_range(end=datetime.now(), periods=800, freq='D')
    
    df = pd.DataFrame({
        'date': random.choices(dates, k=800),
        'country': random.choices(list(COUNTRY_ISO.keys()), k=800),
        'threat_actor': random.choices([
            'LockBit', 'BlackCat', 'Play', 'Cl0p', 'Royal', 'BianLian', 
            'Medusa', 'Akira', 'NoEscape', '8Base', 'Rhysida', 'Hunters',
            'ALPHV', 'Conti', 'Hive'
        ], k=800),
        'threat_type': random.choices([
            'Ransomware', 'Phishing', 'DDoS', 'Malware', 'Data Breach',
            'Credential', 'Vulnerability', 'Defacement', 'Unknown'
        ], weights=[30, 25, 15, 10, 10, 5, 3, 1, 1], k=800),
        'severity': random.choices([
            'Critical', 'High', 'Medium', 'Low', 'Unknown'
        ], weights=[15, 30, 35, 15, 5], k=800),
        'industry': random.choices([
            'Financial', 'Healthcare', 'Government', 'Energy', 'Technology',
            'Telecommunications', 'Education', 'Agriculture', 'Sport', 'Retail'
        ], k=800)
    })
    
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.strftime('%B')
    
    return df

def filter_data(df, year, month, country, threat_type, threat_actor, severity):
    """Apply all filters"""
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
    """Process data for map"""
    map_data = []
    
    for country, iso in COUNTRY_ISO.items():
        country_df = df[df['country'] == country]
        attacks = len(country_df)
        
        top_actors = []
        if not country_df.empty:
            for actor, count in country_df['threat_actor'].value_counts().head(5).items():
                top_actors.append({'name': str(actor), 'count': int(count)})
        
        threat_types = []
        if not country_df.empty:
            for ttype, count in country_df['threat_type'].value_counts().head(3).items():
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
# PDF EXPORT
# ═══════════════════════════════════════════════════════════
def generate_pdf(df, filters):
    """Generate PDF report"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#C41E3A'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    elements.append(Paragraph("CyHawk Africa<br/>Threat Intelligence Report", title_style))
    elements.append(Spacer(1, 12))
    
    meta_style = ParagraphStyle('Meta', parent=styles['Normal'], fontSize=10, textColor=colors.grey)
    meta = Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}<br/>Total Incidents: {len(df)}", meta_style)
    elements.append(meta)
    elements.append(Spacer(1, 20))
    
    summary_data = [
        ['Metric', 'Value'],
        ['Total Incidents', str(len(df))],
        ['Countries', str(df['country'].nunique())],
        ['Threat Actors', str(df['threat_actor'].nunique())],
        ['Critical', str(len(df[df['severity'] == 'Critical']))],
    ]
    
    table = Table(summary_data, colWidths=[3*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#C41E3A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 1, colors.grey)
    ]))
    
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Load data
df = load_data()

# ═══════════════════════════════════════════════════════════
# CSS STYLING
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {{ font-family: 'Inter', sans-serif; -webkit-font-smoothing: antialiased; }}
.stApp {{ background: {C['bg']}; color: {C['text']}; }}
#MainMenu, footer, header {{ visibility: hidden; }}

.stApp::before {{
    content: ''; position: fixed; inset: 0;
    background-image: 
        linear-gradient({C['red_glow']} 1px, transparent 1px),
        linear-gradient(90deg, {C['red_glow']} 1px, transparent 1px);
    background-size: 50px 50px; z-index: -1; opacity: 0.3;
}}

.main-header {{
    background: rgba(10, 10, 10, 0.95); backdrop-filter: blur(20px);
    border-bottom: 1px solid {C['border']}; padding: 1rem 3rem;
    display: flex; justify-content: space-between; align-items: center;
    margin: -6rem -6rem 2rem -6rem;
}}

.logo-section {{ display: flex; align-items: center; gap: 1rem; }}
.logo-container {{
    width: 50px; height: 50px; background: {C['cyhawk_red']};
    border-radius: 50%; box-shadow: 0 0 20px {C['red_glow']};
}}

.brand-text h1 {{ font-size: 1.5rem; font-weight: 600; margin: 0; }}
.brand-highlight {{ color: {C['cyhawk_red']}; font-weight: 700; }}
.brand-text p {{
    font-size: 0.75rem; color: {C['text_dim']};
    text-transform: uppercase; letter-spacing: 2px; margin: 0;
}}

.status-indicator {{
    display: flex; align-items: center; gap: 0.5rem;
    padding: 0.5rem 1rem; background: rgba(0, 255, 0, 0.1);
    border: 1px solid {C['success']}; border-radius: 20px;
}}

.status-dot {{
    width: 8px; height: 8px; background: {C['success']};
    border-radius: 50%; animation: pulse 2s infinite;
}}

@keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} }}

.hero-label {{
    color: {C['cyhawk_red']}; font-size: 0.75rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 2px; margin-bottom: 1rem;
}}
.hero-label::before {{
    content: ''; display: inline-block; width: 30px; height: 2px;
    background: {C['cyhawk_red']}; margin-right: 0.5rem;
}}

.hero-title {{
    font-size: 3.5rem; font-weight: 700; margin-bottom: 1rem;
    letter-spacing: -2px; line-height: 1.1;
}}

.hero-subtitle {{ font-size: 1.25rem; color: {C['text_dim']}; margin-bottom: 2rem; }}

.map-container {{
    background: linear-gradient(135deg, {C['bg_card']} 0%, {C['bg_elevated']} 100%);
    border: 1px solid {C['border']}; border-radius: 24px;
    padding: 3rem; margin-bottom: 2rem; position: relative; overflow: hidden;
}}

.stats-grid {{
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 1.5rem; margin: 2rem 0;
}}

.stat-card {{
    background: {C['bg_card']}; border: 1px solid {C['border']};
    border-radius: 16px; padding: 1.5rem; transition: all 0.3s;
}}

.stat-card:hover {{ border-color: {C['cyhawk_red']}; transform: translateY(-4px); }}

.stat-value {{
    font-size: 2.5rem; font-weight: 700; color: {C['cyhawk_red']};
    line-height: 1; margin-bottom: 0.25rem;
}}

.stat-label {{
    font-size: 0.85rem; color: {C['text_dim']};
    text-transform: uppercase; letter-spacing: 1px;
}}

.legend {{
    display: flex; gap: 2rem; padding: 1.5rem 0;
    border-top: 1px solid {C['border']}; flex-wrap: wrap;
}}

.legend-item {{ display: flex; align-items: center; gap: 0.75rem; }}
.legend-dot {{ width: 12px; height: 12px; border-radius: 50%; }}

.section-header {{ margin: 3rem 0 2rem 0; }}
.section-label {{
    color: {C['cyhawk_red']}; font-size: 0.7rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 2px; margin-bottom: 0.75rem;
}}
.section-title {{ font-size: 2rem; font-weight: 700; }}

.chart-card {{
    background: {C['bg_card']}; border: 1px solid {C['border']};
    border-radius: 20px; padding: 2rem; margin-bottom: 2rem;
    transition: all 0.3s;
}}

.chart-card:hover {{ border-color: rgba(196, 30, 58, 0.5); }}

.chart-header {{
    display: flex; justify-content: space-between;
    align-items: center; margin-bottom: 1.5rem;
}}

.chart-title {{ font-size: 1.1rem; font-weight: 600; }}

.chart-badge {{
    background: rgba(196, 30, 58, 0.1); color: {C['cyhawk_red']};
    padding: 0.4rem 0.9rem; border-radius: 20px;
    font-size: 0.7rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1px;
}}

.filter-container {{
    background: {C['bg_card']}; border: 1px solid {C['border']};
    border-radius: 16px; padding: 1.5rem; margin-bottom: 2rem;
}}

.stSelectbox label {{
    font-size: 0.75rem !important; color: {C['text_subtle']} !important;
    text-transform: uppercase; letter-spacing: 1px; font-weight: 600 !important;
}}

.stButton > button {{
    background: {C['cyhawk_red']} !important; color: white !important;
    border: none !important; border-radius: 12px !important;
    padding: 0.75rem 1.5rem !important; font-weight: 600 !important;
}}

.block-container {{ padding-top: 1rem; max-width: 1400px; }}

@media (max-width: 768px) {{
    .stats-grid {{ grid-template-columns: 1fr; }}
    .hero-title {{ font-size: 2rem; }}
}}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
<div class="main-header">
    <div class="logo-section">
        <div class="logo-container"></div>
        <div class="brand-text">
            <h1><span class="brand-highlight">CyHawk</span> Africa</h1>
            <p>Threat Intelligence Platform</p>
        </div>
    </div>
    <div class="status-indicator">
        <div class="status-dot"></div>
        <span style="color: {C['text_dim']}; font-size: 0.85rem;">Live</span>
    </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    if st.button("🌓 Toggle Theme", use_container_width=True):
        toggle_theme()
        st.rerun()

# ═══════════════════════════════════════════════════════════
# HERO
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero-label">CONTINENTAL INTELLIGENCE</div>
<h1 class="hero-title">Africa Threat Landscape</h1>
<p class="hero-subtitle">Real-time cyber threat monitoring across African nations</p>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# FILTERS
# ═══════════════════════════════════════════════════════════
st.markdown('<div class="filter-container">', unsafe_allow_html=True)

c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    years = ["All Years"] + sorted([str(y) for y in df['year'].unique()], reverse=True)
    year = st.selectbox("Year", years)

with c2:
    months = ["All Months", "January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    month = st.selectbox("Month", months)

with c3:
    countries = ["All Countries"] + sorted(df['country'].unique().tolist())
    country = st.selectbox("Country", countries)

with c4:
    types = ["All Types"] + sorted(df['threat_type'].unique().tolist())
    threat_type = st.selectbox("Threat Type", types)

with c5:
    actors = ["All Actors"] + sorted(df['threat_actor'].unique().tolist())
    actor = st.selectbox("Threat Actor", actors)

with c6:
    sevs = ["All Severities", "Critical", "High", "Medium", "Low"]
    severity = st.selectbox("Severity", sevs)

st.markdown('</div>', unsafe_allow_html=True)

filtered_df = filter_data(df, year, month, country, threat_type, actor, severity)

# ═══════════════════════════════════════════════════════════
# AFRICA MAP
# ═══════════════════════════════════════════════════════════
map_df = process_map_data(filtered_df)

st.markdown('<div class="map-container">', unsafe_allow_html=True)

hover_texts = []
for _, row in map_df.iterrows():
    actors_txt = ""
    if row['top_actors']:
        actors_txt = "<br><b>Top Actors:</b>"
        for a in row['top_actors'][:5]:
            actors_txt += f"<br>  • {a['name']}: {a['count']}"
    
    types_txt = ""
    if row['threat_types']:
        types_txt = "<br><b>Top Threats:</b>"
        for t in row['threat_types'][:3]:
            types_txt += f"<br>  • {t['type']}: {t['count']}"
    
    hover_texts.append(f"<b>{row['country']}</b><br>Attacks: {row['attacks']}{actors_txt}{types_txt}")

fig = go.Figure(go.Choropleth(
    locations=map_df['iso_alpha'], z=map_df['attacks'], locationmode='ISO-3',
    colorscale=[[0, '#0D47A1'], [0.4, '#00E676'], [0.5, '#FFEB3B'], [0.7, '#FF9800'], [1, '#C41E3A']],
    marker=dict(line=dict(color=C['border'], width=0.5)),
    colorbar=dict(title="Threats", titlefont=dict(color=C['text']), tickfont=dict(color=C['text'])),
    text=hover_texts, hovertemplate='%{text}<extra></extra>'
))

fig.update_geos(
    scope='africa', projection_type='natural earth',
    showland=True, landcolor=C['bg_elevated'],
    showocean=True, oceancolor=C['bg'],
    showcountries=True, countrycolor=C['border'], bgcolor=C['bg_card']
)

fig.update_layout(
    height=650, margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor='rgba(0,0,0,0)', geo=dict(bgcolor='rgba(0,0,0,0)'),
    font=dict(color=C['text'])
)

st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# STATS
# ═══════════════════════════════════════════════════════════
total = len(filtered_df)
crit_high = len(filtered_df[filtered_df['severity'].isin(['Critical', 'High'])])
actors_cnt = filtered_df['threat_actor'].nunique()
countries_cnt = filtered_df['country'].nunique()

st.markdown(f"""
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-value">{total}</div>
        <div class="stat-label">Total Threats</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">{crit_high}</div>
        <div class="stat-label">Critical & High</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">{actors_cnt}</div>
        <div class="stat-label">Threat Actors</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">{countries_cnt}</div>
        <div class="stat-label">Countries</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="legend">
    <div class="legend-item"><div class="legend-dot" style="background: #0D47A1;"></div><span>Safe</span></div>
    <div class="legend-item"><div class="legend-dot" style="background: #00E676;"></div><span>Low</span></div>
    <div class="legend-item"><div class="legend-dot" style="background: #FFEB3B;"></div><span>Moderate</span></div>
    <div class="legend-item"><div class="legend-dot" style="background: #FF9800;"></div><span>High</span></div>
    <div class="legend-item"><div class="legend-dot" style="background: #C41E3A;"></div><span>Critical</span></div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# ANALYTICS SECTION 1: TOP RANSOMWARE & THREATS
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
<div class="section-header">
    <div class="section-label">ANALYSIS</div>
    <h2 class="section-title">Threat Intelligence</h2>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="chart-header">
        <h3 class="chart-title">Top Ransomware Groups</h3>
        <span class="chart-badge">Ransomware Activity</span>
    </div>
    """, unsafe_allow_html=True)
    
    ransomware_df = filtered_df[filtered_df['threat_type'] == 'Ransomware']
    ransomware_actors = ransomware_df['threat_actor'].value_counts().head(10)
    
    fig1 = go.Figure(go.Bar(
        y=ransomware_actors.index,
        x=ransomware_actors.values,
        orientation='h',
        marker=dict(color='#C41E3A'),
        hovertemplate='<b>%{y}</b><br>Count: %{x}<extra></extra>'
    ))
    
    fig1.update_layout(
        height=300, margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor=C['border'], showgrid=True, color=C['text']),
        yaxis=dict(gridcolor=C['border'], showgrid=False, color=C['text']),
        font=dict(color=C['text'])
    )
    
    st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="chart-header">
        <h3 class="chart-title">Top Threats</h3>
        <span class="chart-badge">Threat Type Breakdown</span>
    </div>
    """, unsafe_allow_html=True)
    
    threat_counts = filtered_df['threat_type'].value_counts().head(10)
    
    colors_map = {'Ransomware': '#C41E3A', 'Phishing': '#FF9800', 'DDoS': '#FFEB3B', 
                  'Malware': '#00E676', 'Data Breach': '#00BCD4'}
    bar_colors = [colors_map.get(t, '#999999') for t in threat_counts.index]
    
    fig2 = go.Figure(go.Bar(
        x=threat_counts.index,
        y=threat_counts.values,
        marker=dict(color=bar_colors),
        hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
    ))
    
    fig2.update_layout(
        height=300, margin=dict(l=20, r=20, t=20, b=40),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor=C['border'], showgrid=False, color=C['text'], tickangle=-45),
        yaxis=dict(gridcolor=C['border'], showgrid=True, color=C['text']),
        font=dict(color=C['text'])
    )
    
    st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# ANALYTICS SECTION 2: CLASSIFICATION & SEVERITY
# ═══════════════════════════════════════════════════════════
col3, col4 = st.columns(2)

with col3:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="chart-header">
        <h3 class="chart-title">Threat Classification</h3>
        <span class="chart-badge">By Type</span>
    </div>
    """, unsafe_allow_html=True)
    
    class_counts = filtered_df['threat_type'].value_counts()
    
    fig3 = go.Figure(go.Bar(
        y=class_counts.index,
        x=class_counts.values,
        orientation='h',
        marker=dict(color='#C41E3A'),
        hovertemplate='<b>%{y}</b><br>Count: %{x}<extra></extra>'
    ))
    
    fig3.update_layout(
        height=300, margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor=C['border'], showgrid=True, color=C['text']),
        yaxis=dict(gridcolor=C['border'], showgrid=False, color=C['text']),
        font=dict(color=C['text'])
    )
    
    st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="chart-header">
        <h3 class="chart-title">Severity Analysis</h3>
        <span class="chart-badge">Impact Level</span>
    </div>
    """, unsafe_allow_html=True)
    
    sev_counts = filtered_df['severity'].value_counts()
    sev_colors = {'Critical': '#9C27B0', 'Medium': '#FFA726', 'High': '#C41E3A', 'Low': '#66BB6A', 'Unknown': '#757575'}
    sev_bar_colors = [sev_colors.get(s, '#999999') for s in sev_counts.index]
    
    fig4 = go.Figure(go.Bar(
        x=sev_counts.index,
        y=sev_counts.values,
        marker=dict(color=sev_bar_colors),
        hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
    ))
    
    fig4.update_layout(
        height=300, margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor=C['border'], showgrid=False, color=C['text']),
        yaxis=dict(gridcolor=C['border'], showgrid=True, color=C['text']),
        font=dict(color=C['text'])
    )
    
    st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# ANALYTICS SECTION 3: TIMELINE
# ═══════════════════════════════════════════════════════════
st.markdown('<div class="chart-card">', unsafe_allow_html=True)
st.markdown(f"""
<div class="chart-header">
    <h3 class="chart-title">Activity Timeline</h3>
    <span class="chart-badge">Historical Trend</span>
</div>
""", unsafe_allow_html=True)

timeline_df = filtered_df.groupby(filtered_df['date'].dt.to_period('D')).size().reset_index(name='count')
timeline_df['date'] = timeline_df['date'].dt.to_timestamp()

fig5 = go.Figure(go.Scatter(
    x=timeline_df['date'],
    y=timeline_df['count'],
    mode='lines',
    line=dict(color='#C41E3A', width=2),
    fill='tozeroy',
    fillcolor='rgba(196, 30, 58, 0.1)',
    hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Count: %{y}<extra></extra>'
))

fig5.update_layout(
    height=250, margin=dict(l=20, r=20, t=20, b=20),
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(gridcolor=C['border'], showgrid=True, color=C['text']),
    yaxis=dict(gridcolor=C['border'], showgrid=True, color=C['text']),
    font=dict(color=C['text'])
)

st.plotly_chart(fig5, use_container_width=True, config={'displayModeBar': False})
st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# ANALYTICS SECTION 4: ACTORS & INDUSTRIES
# ═══════════════════════════════════════════════════════════
col5, col6 = st.columns(2)

with col5:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="chart-header">
        <h3 class="chart-title">Top Threat Actors</h3>
        <span class="chart-badge">Most Active</span>
    </div>
    """, unsafe_allow_html=True)
    
    top_actors = filtered_df['threat_actor'].value_counts().head(10)
    
    fig6 = go.Figure(go.Bar(
        y=top_actors.index,
        x=top_actors.values,
        orientation='h',
        marker=dict(color='#C41E3A'),
        hovertemplate='<b>%{y}</b><br>Count: %{x}<extra></extra>'
    ))
    
    fig6.update_layout(
        height=300, margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor=C['border'], showgrid=True, color=C['text']),
        yaxis=dict(gridcolor=C['border'], showgrid=False, color=C['text']),
        font=dict(color=C['text'])
    )
    
    st.plotly_chart(fig6, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with col6:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="chart-header">
        <h3 class="chart-title">Most Targeted Industries</h3>
        <span class="chart-badge">Sector Analysis</span>
    </div>
    """, unsafe_allow_html=True)
    
    industries = filtered_df['industry'].value_counts().head(10)
    
    fig7 = go.Figure(go.Bar(
        y=industries.index,
        x=industries.values,
        orientation='h',
        marker=dict(color='#C41E3A'),
        hovertemplate='<b>%{y}</b><br>Count: %{x}<extra></extra>'
    ))
    
    fig7.update_layout(
        height=300, margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor=C['border'], showgrid=True, color=C['text']),
        yaxis=dict(gridcolor=C['border'], showgrid=False, color=C['text']),
        font=dict(color=C['text'])
    )
    
    st.plotly_chart(fig7, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# PDF EXPORT
# ═══════════════════════════════════════════════════════════
st.markdown("---")
c_a, c_b = st.columns([3, 1])
with c_b:
    if st.button("📥 Export PDF Report", type="primary", use_container_width=True):
        filters_applied = {
            'Year': year, 'Month': month, 'Country': country,
            'Type': threat_type, 'Actor': actor, 'Severity': severity
        }
        pdf_buf = generate_pdf(filtered_df, filters_applied)
        st.download_button(
            "📄 Download PDF",
            data=pdf_buf,
            file_name=f"cyhawk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
