import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import base64

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="CyHawk Africa - Threat Intelligence Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------
# THEME STATE & TOGGLE
# --------------------------------------------------
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    """Toggle between dark and light mode"""
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# --------------------------------------------------
# THEME COLORS - V3 Modern Minimalist
# --------------------------------------------------
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
        'chart_template': 'plotly_dark',
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
        'chart_template': 'plotly_white',
    }
}

C = THEMES[st.session_state.theme]

# --------------------------------------------------
# CUSTOM CSS - V3 MODERN MINIMALIST DESIGN
# --------------------------------------------------
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* ============================================
       GLOBAL STYLES
       ============================================ */
    * {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        -webkit-font-smoothing: antialiased;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    
    .stApp {{
        background: {C['bg']};
        color: {C['text']};
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Subtle grid background */
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
    
    /* ============================================
       HEADER / NAVIGATION
       ============================================ */
    .main-header {{
        background: rgba({C['bg_elevated'].replace('#', '')}, 0.95);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid {C['border']};
        padding: 1rem 3rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: sticky;
        top: 0;
        z-index: 1000;
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
        flex-shrink: 0;
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
        letter-spacing: -0.5px;
        margin: 0;
        line-height: 1.2;
    }}
    
    .brand-text h1 .brand-highlight {{
        color: {C['cyhawk_red']};
        font-weight: 700;
    }}
    
    .brand-text p {{
        font-size: 0.75rem;
        color: {C['text_dim']};
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 2px;
    }}
    
    .header-nav {{
        display: flex;
        gap: 2rem;
        align-items: center;
    }}
    
    .nav-item {{
        color: {C['text_dim']};
        font-size: 0.9rem;
        font-weight: 500;
        cursor: pointer;
        transition: color 0.2s;
        text-decoration: none;
    }}
    
    .nav-item:hover {{
        color: {C['text']};
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
    
    .time-badge {{
        background: {C['bg_card']};
        border: 1px solid {C['border']};
        border-radius: 20px;
        padding: 0.5rem 1rem;
        color: {C['text_dim']};
        font-size: 0.85rem;
        font-weight: 500;
    }}
    
    /* ============================================
       HERO SECTION
       ============================================ */
    .hero-section {{
        margin-bottom: 3rem;
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
        max-width: 700px;
        margin-bottom: 2rem;
    }}
    
    /* ============================================
       MAP CONTAINER
       ============================================ */
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
    
    /* ============================================
       MAP STATS GRID
       ============================================ */
    .map-stats-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        margin-top: 2rem;
    }}
    
    .map-stat-card {{
        background: {C['bg_card']};
        backdrop-filter: blur(20px);
        border: 1px solid {C['border']};
        border-radius: 16px;
        padding: 1.5rem;
        transition: all 0.3s ease;
    }}
    
    .map-stat-card:hover {{
        border-color: {C['cyhawk_red']};
        transform: translateY(-4px);
    }}
    
    .map-stat-value {{
        font-size: 2.5rem;
        font-weight: 700;
        color: {C['cyhawk_red']};
        margin-bottom: 0.25rem;
        line-height: 1;
    }}
    
    .map-stat-label {{
        font-size: 0.85rem;
        color: {C['text_dim']};
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    /* ============================================
       LEGEND
       ============================================ */
    .legend-container {{
        display: flex;
        gap: 3rem;
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
    
    /* ============================================
       METRICS GRID
       ============================================ */
    .metrics-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        margin-bottom: 4rem;
    }}
    
    .metric-card {{
        background: {C['bg_card']};
        border: 1px solid {C['border']};
        border-radius: 20px;
        padding: 2rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }}
    
    .metric-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, {C['cyhawk_red']} 0%, transparent 100%);
        opacity: 0;
        transition: opacity 0.3s;
    }}
    
    .metric-card:hover {{
        border-color: {C['cyhawk_red']};
        transform: translateY(-4px);
    }}
    
    .metric-card:hover::before {{
        opacity: 1;
    }}
    
    .metric-label {{
        font-size: 0.8rem;
        color: {C['text_subtle']};
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 1rem;
        font-weight: 600;
    }}
    
    .metric-value {{
        font-size: 3rem;
        font-weight: 700;
        color: {C['text']};
        margin-bottom: 0.5rem;
        line-height: 1;
    }}
    
    .metric-change {{
        font-size: 0.85rem;
        color: {C['cyhawk_red']};
        font-weight: 500;
    }}
    
    /* ============================================
       SECTION HEADERS
       ============================================ */
    .section-header {{
        margin-bottom: 2rem;
        margin-top: 1rem;
    }}
    
    .section-label {{
        color: {C['cyhawk_red']};
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 0.75rem;
    }}
    
    .section-title {{
        font-size: 2rem;
        font-weight: 700;
        color: {C['text']};
        letter-spacing: -1px;
    }}
    
    /* ============================================
       CHART CARDS
       ============================================ */
    .chart-card {{
        background: {C['bg_card']};
        border: 1px solid {C['border']};
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        transition: all 0.3s ease;
    }}
    
    .chart-card:hover {{
        border-color: rgba(196, 30, 58, 0.5);
    }}
    
    .chart-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }}
    
    .chart-title {{
        font-size: 1.1rem;
        font-weight: 600;
        color: {C['text']};
    }}
    
    .chart-badge {{
        background: rgba(196, 30, 58, 0.1);
        color: {C['cyhawk_red']};
        padding: 0.4rem 0.9rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    /* ============================================
       FILTERS
       ============================================ */
    .filter-container {{
        background: {C['bg_card']};
        border: 1px solid {C['border']};
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }}
    
    .filter-label {{
        font-size: 0.85rem;
        color: {C['text_subtle']};
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }}
    
    /* ============================================
       FOOTER
       ============================================ */
    .footer {{
        margin-top: 6rem;
        padding: 3rem 0;
        border-top: 1px solid {C['border']};
        text-align: center;
    }}
    
    .footer-logo {{
        font-size: 1.1rem;
        font-weight: 600;
        color: {C['text_dim']};
        margin-bottom: 1rem;
    }}
    
    .footer-logo .brand-highlight {{
        color: {C['cyhawk_red']};
    }}
    
    .footer-links {{
        display: flex;
        gap: 2rem;
        justify-content: center;
        margin-bottom: 1rem;
        flex-wrap: wrap;
    }}
    
    .footer-link {{
        color: {C['text_subtle']};
        font-size: 0.85rem;
        cursor: pointer;
        transition: color 0.2s;
        text-decoration: none;
    }}
    
    .footer-link:hover {{
        color: {C['text_dim']};
    }}
    
    .footer-credits {{
        font-size: 0.75rem;
        color: {C['text_subtle']};
        margin-top: 1rem;
    }}
    
    .footer-status {{
        display: flex;
        gap: 2rem;
        justify-content: center;
        margin-top: 1rem;
        font-size: 0.75rem;
        color: {C['text_subtle']};
    }}
    
    /* ============================================
       PLOTLY CHART CUSTOMIZATION
       ============================================ */
    .js-plotly-plot {{
        background: transparent !important;
    }}
    
    .js-plotly-plot .plotly .modebar {{
        display: none !important;
    }}
    
    /* ============================================
       STREAMLIT OVERRIDES
       ============================================ */
    .block-container {{
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 1400px;
    }}
    
    /* Streamlit columns */
    .stColumn {{
        padding: 0 0.5rem;
    }}
    
    /* Streamlit selectbox */
    .stSelectbox label {{
        font-size: 0.85rem;
        color: {C['text_subtle']};
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }}
    
    /* Streamlit button */
    .stButton > button {{
        background: {C['bg_card']};
        border: 1px solid {C['border']};
        border-radius: 12px;
        color: {C['text']};
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s;
    }}
    
    .stButton > button:hover {{
        border-color: {C['cyhawk_red']};
        background: {C['bg_elevated']};
    }}
    
    /* ============================================
       RESPONSIVE DESIGN
       ============================================ */
    @media (max-width: 1024px) {{
        .metrics-grid {{
            grid-template-columns: repeat(2, 1fr);
        }}
        
        .map-stats-grid {{
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
        
        .header-nav {{
            width: 100%;
            justify-content: space-between;
            gap: 1rem;
        }}
        
        .nav-item {{
            font-size: 0.8rem;
        }}
        
        .hero-title {{
            font-size: 2rem;
        }}
        
        .hero-subtitle {{
            font-size: 1rem;
        }}
        
        .metrics-grid {{
            grid-template-columns: 1fr;
        }}
        
        .map-stats-grid {{
            grid-template-columns: 1fr;
        }}
        
        .legend-container {{
            gap: 1.5rem;
        }}
        
        .map-container {{
            padding: 1.5rem;
        }}
        
        .block-container {{
            padding-left: 1rem;
            padding-right: 1rem;
        }}
    }}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
current_time = datetime.now().strftime("%H:%M UTC")

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
    <div class="header-nav">
        <span class="nav-item">Dashboard</span>
        <span class="nav-item">Threats</span>
        <span class="nav-item">Analytics</span>
        <div class="status-indicator">
            <div class="status-dot"></div>
            <span style="color: {C['text_dim']}; font-size: 0.85rem; font-weight: 500;">Live</span>
        </div>
        <div class="time-badge">{current_time}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Theme toggle in sidebar
with st.sidebar:
    st.markdown("### Theme")
    if st.button("🌓 Toggle Dark/Light Mode", key="theme_toggle", use_container_width=True):
        toggle_theme()
        st.rerun()

# --------------------------------------------------
# DATA GENERATION FUNCTION
# --------------------------------------------------
def generate_sample_data():
    """Generate comprehensive sample threat data for Africa"""
    
    # African countries with ISO-3 codes
    countries = {
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
    
    # Generate country threat data with top actors
    threat_data = []
    for country, iso in countries.items():
        attacks = random.randint(0, 50)
        
        # Generate top 5 threat actors for this country
        all_actors = ['LockBit', 'BlackCat', 'Play', 'Cl0p', 'Royal', 'BianLian', 
                      'Medusa', 'Akira', 'NoEscape', '8Base', 'Rhysida', 'Hunters']
        
        top_actors = []
        selected_actors = random.sample(all_actors, min(5, len(all_actors)))
        for actor in selected_actors:
            top_actors.append({
                'name': actor,
                'count': random.randint(1, 10)
            })
        
        # Sort by count
        top_actors = sorted(top_actors, key=lambda x: x['count'], reverse=True)
        
        # Generate top 3 threat types
        threat_types = []
        types = ['Ransomware', 'Phishing', 'DDoS', 'Data Breach', 'Malware']
        selected_types = random.sample(types, min(3, len(types)))
        for ttype in selected_types:
            threat_types.append({
                'type': ttype,
                'count': random.randint(1, 15)
            })
        
        threat_types = sorted(threat_types, key=lambda x: x['count'], reverse=True)
        
        threat_data.append({
            'country': country,
            'iso_alpha': iso,
            'attacks': attacks,
            'top_actors': top_actors,
            'threat_types': threat_types
        })
    
    map_df = pd.DataFrame(threat_data)
    
    # Threat actors data
    actors = ['LockBit', 'BlackCat', 'Play', 'Cl0p', 'Royal', 'BianLian', 
              'Medusa', 'Akira', 'NoEscape', '8Base', 'Rhysida', 'Hunters International']
    
    actor_data = []
    for actor in actors:
        actor_data.append({
            'actor': actor,
            'attacks': random.randint(15, 85),
            'countries': random.randint(3, 18)
        })
    
    actors_df = pd.DataFrame(actor_data).sort_values('attacks', ascending=False).head(10)
    
    # Timeline data (30 days)
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    timeline_data = []
    for date in dates:
        timeline_data.append({
            'date': date,
            'Ransomware': random.randint(5, 30),
            'Phishing': random.randint(15, 50),
            'DDoS': random.randint(3, 25),
            'Data Breach': random.randint(2, 20),
            'Malware': random.randint(5, 30)
        })
    
    timeline_df = pd.DataFrame(timeline_data)
    
    # Industry data
    industries = ['Financial Services', 'Healthcare', 'Government', 'Energy', 
                  'Telecommunications', 'Education', 'Manufacturing', 'Retail',
                  'Technology', 'Transportation']
    
    industry_data = []
    for industry in industries:
        industry_data.append({
            'industry': industry,
            'attacks': random.randint(25, 120)
        })
    
    industry_df = pd.DataFrame(industry_data).sort_values('attacks', ascending=True)
    
    # Threat classification
    classification = {
        'Ransomware': random.randint(150, 200),
        'Phishing': random.randint(140, 180),
        'DDoS': random.randint(80, 120),
        'Data Breach': random.randint(70, 110),
        'Malware': random.randint(50, 90)
    }
    
    # Severity data
    severity = {
        'Critical': random.randint(120, 170),
        'High': random.randint(200, 280),
        'Medium': random.randint(130, 180),
        'Low': random.randint(40, 80)
    }
    
    return map_df, actors_df, timeline_df, industry_df, classification, severity

# Generate all data
map_df, actors_df, timeline_df, industry_df, classification_data, severity_data = generate_sample_data()

# Calculate metrics
total_threats = map_df['attacks'].sum()
high_severity = int(total_threats * 0.25)
threat_actors_count = len(actors_df)
countries_affected = len(map_df[map_df['attacks'] > 0])

# --------------------------------------------------
# HERO SECTION
# --------------------------------------------------
st.markdown(f"""
<div class="hero-section">
    <div class="hero-label">CONTINENTAL INTELLIGENCE</div>
    <h1 class="hero-title">Africa Threat<br>Landscape</h1>
    <p class="hero-subtitle">
        Real-time cyber threat monitoring across 54 African nations with advanced intelligence analytics and threat actor profiling.
    </p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# AFRICA THREAT MAP (TOP POSITION - HERO)
# --------------------------------------------------
st.markdown('<div class="map-container"><div class="map-inner">', unsafe_allow_html=True)

# Create the map
fig_map = go.Figure()

if not map_df.empty and 'iso_alpha' in map_df.columns:
    # Create hover text with top actors and threat types
    hover_texts = []
    for idx, row in map_df.iterrows():
        country_name = row['country']
        total_attacks = row['attacks']
        
        # Build top actors text
        actors_text = ""
        if row['top_actors']:
            actors_text = "<br><b>Top Threat Actors:</b>"
            for actor in row['top_actors'][:5]:
                actors_text += f"<br>  • {actor['name']}: {actor['count']}"
        
        # Build threat types text
        types_text = ""
        if row['threat_types']:
            types_text = "<br><b>Top Threats:</b>"
            for ttype in row['threat_types'][:3]:
                types_text += f"<br>  • {ttype['type']}: {ttype['count']}"
        
        hover_text = f"<b>{country_name}</b><br>Total Attacks: {total_attacks}{actors_text}{types_text}"
        hover_texts.append(hover_text)
    
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
    geo=dict(
        bgcolor='rgba(0,0,0,0)',
    ),
    font=dict(color=C['text'])
)

st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False}, key='africa_map')

st.markdown('</div></div>', unsafe_allow_html=True)

# Map Stats Grid (below map)
st.markdown(f"""
<div class="map-stats-grid">
    <div class="map-stat-card">
        <div class="map-stat-value">{total_threats}</div>
        <div class="map-stat-label">Active Threats</div>
    </div>
    <div class="map-stat-card">
        <div class="map-stat-value">{high_severity}</div>
        <div class="map-stat-label">Critical</div>
    </div>
    <div class="map-stat-card">
        <div class="map-stat-value">{threat_actors_count}</div>
        <div class="map-stat-label">Actors</div>
    </div>
    <div class="map-stat-card">
        <div class="map-stat-value">{countries_affected}</div>
        <div class="map-stat-label">Countries</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Legend
st.markdown(f"""
<div class="legend-container">
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

# --------------------------------------------------
# FILTERS
# --------------------------------------------------
st.markdown('<div class="filter-container">', unsafe_allow_html=True)

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    st.markdown(f'<div class="filter-label">Time Period</div>', unsafe_allow_html=True)
    time_period = st.selectbox(
        "Time Period",
        ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last 90 Days"],
        index=2,
        label_visibility="collapsed"
    )

with col_f2:
    st.markdown(f'<div class="filter-label">Threat Type</div>', unsafe_allow_html=True)
    threat_type = st.selectbox(
        "Threat Type",
        ["All Types", "Ransomware", "Phishing", "DDoS", "Data Breach", "Malware"],
        label_visibility="collapsed"
    )

with col_f3:
    st.markdown(f'<div class="filter-label">Severity</div>', unsafe_allow_html=True)
    severity_filter = st.selectbox(
        "Severity",
        ["All Severities", "Critical", "High", "Medium", "Low"],
        label_visibility="collapsed"
    )

st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# KEY METRICS
# --------------------------------------------------
st.markdown(f"""
<div class="metrics-grid">
    <div class="metric-card">
        <div class="metric-label">Total Threats</div>
        <div class="metric-value">{total_threats}</div>
        <div class="metric-change">+12 Today</div>
    </div>
    
    <div class="metric-card">
        <div class="metric-label">High Severity</div>
        <div class="metric-value">{high_severity}</div>
        <div class="metric-change">+3 Today</div>
    </div>
    
    <div class="metric-card">
        <div class="metric-label">Threat Actors</div>
        <div class="metric-value">{threat_actors_count}</div>
        <div class="metric-change">Active Now</div>
    </div>
    
    <div class="metric-card">
        <div class="metric-label">Coverage</div>
        <div class="metric-value">{countries_affected}</div>
        <div class="metric-change">Countries</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# THREAT INTELLIGENCE SECTION
# --------------------------------------------------
st.markdown(f"""
<div class="section-header">
    <div class="section-label">ANALYSIS</div>
    <h2 class="section-title">Threat Intelligence</h2>
</div>
""", unsafe_allow_html=True)

# Row 1: Classification & Trends
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="chart-header">
        <h3 class="chart-title">Threat Classification</h3>
        <span class="chart-badge">Live</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Donut chart
    fig_class = go.Figure(data=[go.Pie(
        labels=list(classification_data.keys()),
        values=list(classification_data.values()),
        hole=0.5,
        marker=dict(
            colors=['#C41E3A', '#FF5722', '#FF9800', '#FFC107', '#FFEB3B'],
            line=dict(color=C['bg'], width=2)
        ),
        textfont=dict(color=C['text'], size=12),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
    )])
    
    fig_class.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(
            font=dict(color=C['text'], size=10),
            bgcolor='rgba(0,0,0,0)',
            orientation='h',
            yanchor='bottom',
            y=-0.2,
            xanchor='center',
            x=0.5
        ),
        font=dict(color=C['text'])
    )
    
    st.plotly_chart(fig_class, use_container_width=True, config={'displayModeBar': False}, key='chart_classification')
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="chart-header">
        <h3 class="chart-title">Attack Trends</h3>
        <span class="chart-badge">30 Days</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Stacked area chart
    fig_timeline = go.Figure()
    
    colors = ['#C41E3A', '#FF9800', '#FFEB3B', '#00E676', '#00BCD4']
    categories = ['Ransomware', 'Phishing', 'DDoS', 'Data Breach', 'Malware']
    
    for i, category in enumerate(categories):
        fig_timeline.add_trace(go.Scatter(
            x=timeline_df['date'],
            y=timeline_df[category],
            mode='lines',
            name=category,
            line=dict(color=colors[i], width=2),
            fill='tonexty' if i > 0 else 'tozeroy',
            stackgroup='one',
            hovertemplate='<b>%{fullData.name}</b><br>%{x|%b %d}<br>Attacks: %{y}<extra></extra>'
        ))
    
    fig_timeline.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            gridcolor=C['border'],
            showgrid=True,
            color=C['text'],
            title=None
        ),
        yaxis=dict(
            gridcolor=C['border'],
            showgrid=True,
            color=C['text'],
            title=None
        ),
        showlegend=True,
        legend=dict(
            font=dict(color=C['text'], size=9),
            bgcolor='rgba(0,0,0,0)',
            orientation='h',
            yanchor='bottom',
            y=-0.3,
            xanchor='center',
            x=0.5
        ),
        hovermode='x unified',
        font=dict(color=C['text'])
    )
    
    st.plotly_chart(fig_timeline, use_container_width=True, config={'displayModeBar': False}, key='chart_timeline')
    st.markdown('</div>', unsafe_allow_html=True)

# Row 2: Top Actors & Industries
col3, col4 = st.columns(2)

with col3:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="chart-header">
        <h3 class="chart-title">Top Threat Actors</h3>
        <span class="chart-badge">Most Active</span>
    </div>
    """, unsafe_allow_html=True)
    
    fig_actors = go.Figure()
    
    fig_actors.add_trace(go.Bar(
        y=actors_df['actor'],
        x=actors_df['attacks'],
        orientation='h',
        marker=dict(
            color=actors_df['attacks'],
            colorscale=[[0, '#00E676'], [0.5, '#FF9800'], [1, '#C41E3A']],
            line=dict(color=C['border'], width=1)
        ),
        hovertemplate='<b>%{y}</b><br>Attacks: %{x}<extra></extra>',
        showlegend=False
    ))
    
    fig_actors.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            gridcolor=C['border'],
            showgrid=True,
            color=C['text'],
            title=None
        ),
        yaxis=dict(
            gridcolor=C['border'],
            showgrid=False,
            color=C['text'],
            title=None
        ),
        font=dict(color=C['text'])
    )
    
    st.plotly_chart(fig_actors, use_container_width=True, config={'displayModeBar': False}, key='chart_actors')
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="chart-header">
        <h3 class="chart-title">Targeted Industries</h3>
        <span class="chart-badge">Sector Analysis</span>
    </div>
    """, unsafe_allow_html=True)
    
    fig_industry = go.Figure()
    
    fig_industry.add_trace(go.Bar(
        y=industry_df['industry'],
        x=industry_df['attacks'],
        orientation='h',
        marker=dict(
            color='#C41E3A',
            line=dict(color=C['border'], width=1)
        ),
        hovertemplate='<b>%{y}</b><br>Attacks: %{x}<extra></extra>',
        showlegend=False
    ))
    
    fig_industry.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            gridcolor=C['border'],
            showgrid=True,
            color=C['text'],
            title=None
        ),
        yaxis=dict(
            gridcolor=C['border'],
            showgrid=False,
            color=C['text'],
            title=None
        ),
        font=dict(color=C['text'])
    )
    
    st.plotly_chart(fig_industry, use_container_width=True, config={'displayModeBar': False}, key='chart_industry')
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# RANSOMWARE INTELLIGENCE SECTION
# --------------------------------------------------
st.markdown(f"""
<div class="section-header">
    <div class="section-label">CRITICAL</div>
    <h2 class="section-title">Ransomware Intelligence</h2>
</div>
""", unsafe_allow_html=True)

col5, col6 = st.columns(2)

with col5:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="chart-header">
        <h3 class="chart-title">Active Ransomware Groups</h3>
        <span class="chart-badge">Critical</span>
    </div>
    """, unsafe_allow_html=True)
    
    ransomware_groups = actors_df.head(8).copy()
    
    fig_ransomware = go.Figure()
    
    fig_ransomware.add_trace(go.Bar(
        x=ransomware_groups['actor'],
        y=ransomware_groups['attacks'],
        marker=dict(
            color=ransomware_groups['attacks'],
            colorscale=[[0, '#FF9800'], [1, '#C41E3A']],
            line=dict(color=C['border'], width=1)
        ),
        hovertemplate='<b>%{x}</b><br>Attacks: %{y}<extra></extra>',
        showlegend=False
    ))
    
    fig_ransomware.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=20, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            gridcolor=C['border'],
            showgrid=False,
            color=C['text'],
            title=None,
            tickangle=-45
        ),
        yaxis=dict(
            gridcolor=C['border'],
            showgrid=True,
            color=C['text'],
            title=None
        ),
        font=dict(color=C['text'])
    )
    
    st.plotly_chart(fig_ransomware, use_container_width=True, config={'displayModeBar': False}, key='chart_ransomware')
    st.markdown('</div>', unsafe_allow_html=True)

with col6:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="chart-header">
        <h3 class="chart-title">Severity Assessment</h3>
        <span class="chart-badge">Impact Analysis</span>
    </div>
    """, unsafe_allow_html=True)
    
    fig_severity = go.Figure()
    
    fig_severity.add_trace(go.Bar(
        x=list(severity_data.keys()),
        y=list(severity_data.values()),
        marker=dict(
            color=['#C41E3A', '#FF9800', '#FFC107', '#00E676'],
            line=dict(color=C['border'], width=1)
        ),
        hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>',
        showlegend=False
    ))
    
    fig_severity.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            gridcolor=C['border'],
            showgrid=False,
            color=C['text'],
            title=None
        ),
        yaxis=dict(
            gridcolor=C['border'],
            showgrid=True,
            color=C['text'],
            title=None
        ),
        font=dict(color=C['text'])
    )
    
    st.plotly_chart(fig_severity, use_container_width=True, config={'displayModeBar': False}, key='chart_severity')
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# EXPORT FUNCTIONALITY
# --------------------------------------------------
st.markdown("---")

export_col1, export_col2 = st.columns([3, 1])

with export_col2:
    if st.button("📥 Export Data (CSV)", use_container_width=True):
        # Prepare export data
        export_df = map_df[['country', 'iso_alpha', 'attacks']].copy()
        export_df['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        csv = export_df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        filename = f"cyhawk_threats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        st.markdown(f"""
        <a href="data:file/csv;base64,{b64}" download="{filename}" 
           style="display: inline-block; padding: 0.5rem 1rem; background: {C['cyhawk_red']}; 
                  color: white; text-decoration: none; border-radius: 8px; font-weight: 500;">
            Download {filename}
        </a>
        """, unsafe_allow_html=True)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
system_uptime = "99.8%"
last_sync = datetime.now().strftime("%Y-%m-%d %H:%M UTC")

st.markdown(f"""
<div class="footer">
    <div class="footer-logo">
        <span class="brand-highlight">CyHawk</span> Africa
    </div>
    <div class="footer-links">
        <a href="#" class="footer-link">About</a>
        <a href="#" class="footer-link">Documentation</a>
        <a href="#" class="footer-link">API</a>
        <a href="#" class="footer-link">Contact</a>
        <a href="#" class="footer-link">Privacy Policy</a>
    </div>
    <div class="footer-status">
        <span>System Uptime: {system_uptime}</span>
        <span>•</span>
        <span>Last Sync: {last_sync}</span>
        <span>•</span>
        <span>Status: Operational</span>
    </div>
    <div class="footer-credits">
        © 2025 CyHawk Africa. All Rights Reserved.
    </div>
</div>
""", unsafe_allow_html=True)
