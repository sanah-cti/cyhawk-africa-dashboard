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
# DATA LOADING
# ═══════════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def load_data():
    """Load incidents data from CSV with fallback"""
    
    country_iso = {
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
    
    try:
        if os.path.exists('data/incidents.csv'):
            df = pd.read_csv('data/incidents.csv')
        elif os.path.exists('../data/incidents.csv'):
            df = pd.read_csv('../data/incidents.csv')
        else:
            raise FileNotFoundError()
        
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.strftime('%B')
        
        return df, country_iso
        
    except:
        import random
        from datetime import timedelta
        
        dates = pd.date_range(end=datetime.now(), periods=500, freq='D')
        df = pd.DataFrame({
            'date': random.choices(dates, k=500),
            'country': random.choices(list(country_iso.keys()), k=500),
            'threat_actor': random.choices(['LockBit', 'BlackCat', 'Play', 'Cl0p', 'Royal'], k=500),
            'threat_type': random.choices(['Ransomware', 'Phishing', 'DDoS', 'Malware'], k=500),
            'severity': random.choices(['Critical', 'High', 'Medium', 'Low'], k=500),
        })
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.strftime('%B')
        
        return df, country_iso

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

def process_map_data(df, country_iso):
    """Process data for map"""
    map_data = []
    
    for country, iso in country_iso.items():
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
def generate_pdf(df):
    """Generate PDF report"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#C41E3A'),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    elements.append(Paragraph("CyHawk Africa<br/>Threat Intelligence Report", title_style))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    data = [
        ['Metric', 'Value'],
        ['Total Incidents', str(len(df))],
        ['Countries', str(df['country'].nunique())],
        ['Threat Actors', str(df['threat_actor'].nunique())],
        ['Critical', str(len(df[df['severity'] == 'Critical']))],
    ]
    
    table = Table(data, colWidths=[3*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#C41E3A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 1, colors.grey)
    ]))
    
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer

# ═══════════════════════════════════════════════════════════
# LOAD DATA
# ═══════════════════════════════════════════════════════════
df, country_iso = load_data()

# ═══════════════════════════════════════════════════════════
# CSS STYLING
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {{ font-family: 'Inter', sans-serif; }}
.stApp {{ background: {C['bg']}; color: {C['text']}; }}
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
    background: {C['bg_elevated']};
    border-bottom: 1px solid {C['border']};
    padding: 1rem 3rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: -6rem -6rem 2rem -6rem;
}}

.logo-section {{ display: flex; align-items: center; gap: 1rem; }}
.logo-container {{
    width: 50px;
    height: 50px;
    background: {C['cyhawk_red']};
    border-radius: 50%;
    box-shadow: 0 0 20px {C['red_glow']};
}}

.brand-text h1 {{ 
    font-size: 1.5rem; 
    font-weight: 600; 
    margin: 0;
}}
.brand-highlight {{ color: {C['cyhawk_red']}; font-weight: 700; }}
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
}}

.hero-label::before {{
    content: '';
    display: inline-block;
    width: 30px;
    height: 2px;
    background: {C['cyhawk_red']};
    margin-right: 0.5rem;
}}

.hero-title {{
    font-size: 3.5rem;
    font-weight: 700;
    margin-bottom: 1rem;
    letter-spacing: -2px;
}}

.hero-subtitle {{
    font-size: 1.25rem;
    color: {C['text_dim']};
    margin-bottom: 2rem;
}}

.map-container {{
    background: linear-gradient(135deg, {C['bg_card']} 0%, {C['bg_elevated']} 100%);
    border: 1px solid {C['border']};
    border-radius: 24px;
    padding: 3rem;
    margin-bottom: 2rem;
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
    transition: all 0.3s;
}}

.stat-card:hover {{
    border-color: {C['cyhawk_red']};
    transform: translateY(-4px);
}}

.stat-value {{
    font-size: 2.5rem;
    font-weight: 700;
    color: {C['cyhawk_red']};
    line-height: 1;
}}

.stat-label {{
    font-size: 0.85rem;
    color: {C['text_dim']};
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 0.5rem;
}}

.legend {{
    display: flex;
    gap: 2rem;
    padding: 1.5rem 0;
    border-top: 1px solid {C['border']};
    flex-wrap: wrap;
}}

.legend-item {{ display: flex; align-items: center; gap: 0.75rem; }}
.legend-dot {{ width: 12px; height: 12px; border-radius: 50%; }}

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
# FILTERS (6 DROPDOWNS)
# ═══════════════════════════════════════════════════════════
st.markdown('<div class="filter-container">', unsafe_allow_html=True)

c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    years = ["All Years"] + sorted([str(y) for y in df['year'].unique()], reverse=True)
    year = st.selectbox("Year", years)

with c2:
    months = ["All Months"] + ["January", "February", "March", "April", "May", "June",
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

# Apply filters
filtered_df = filter_data(df, year, month, country, threat_type, actor, severity)

# ═══════════════════════════════════════════════════════════
# MAP
# ═══════════════════════════════════════════════════════════
map_df = process_map_data(filtered_df, country_iso)

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
    locations=map_df['iso_alpha'],
    z=map_df['attacks'],
    locationmode='ISO-3',
    colorscale=[[0, '#0D47A1'], [0.4, '#00E676'], [0.5, '#FFEB3B'], [0.7, '#FF9800'], [1, '#C41E3A']],
    marker=dict(line=dict(color=C['border'], width=0.5)),
    colorbar=dict(
        title="Threats",
        titlefont=dict(color=C['text']),
        tickfont=dict(color=C['text']),
        bgcolor=C['bg_card']
    ),
    text=hover_texts,
    hovertemplate='%{text}<extra></extra>'
))

fig.update_geos(
    scope='africa',
    projection_type='natural earth',
    showland=True,
    landcolor=C['bg_elevated'],
    showocean=True,
    oceancolor=C['bg'],
    showcountries=True,
    countrycolor=C['border'],
    bgcolor=C['bg_card']
)

fig.update_layout(
    height=650,
    margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor='rgba(0,0,0,0)',
    geo=dict(bgcolor='rgba(0,0,0,0)'),
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

# Legend
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
# PDF EXPORT
# ═══════════════════════════════════════════════════════════
st.markdown("---")
c_a, c_b = st.columns([3, 1])
with c_b:
    if st.button("📥 Export PDF Report", type="primary", use_container_width=True):
        pdf_buf = generate_pdf(filtered_df)
        st.download_button(
            label="📄 Download PDF",
            data=pdf_buf,
            file_name=f"cyhawk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
