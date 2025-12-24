import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random

# Page config
st.set_page_config(
    page_title="CyHawk Africa - Threat Intelligence Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state for theme
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    """Toggle between dark and light mode"""
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# Theme colors
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

# Get current theme
C = THEMES[st.session_state.theme]

# Custom CSS - V3 Modern Minimalist Design
st.markdown(f"""
<style>
    /* Global Styles */
    .stApp {{
        background: {C['bg']};
        color: {C['text']};
    }}
    
    /* Hide Streamlit default elements */
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
    
    /* Header */
    .main-header {{
        background: {C['bg_elevated']};
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
        width: 45px;
        height: 45px;
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
        letter-spacing: -0.5px;
        margin: 0;
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
    
    .theme-toggle {{
        background: {C['bg_card']};
        border: 1px solid {C['border']};
        border-radius: 20px;
        padding: 0.5rem 1rem;
        cursor: pointer;
        color: {C['text_dim']};
        font-size: 0.9rem;
        transition: all 0.2s;
    }}
    
    .theme-toggle:hover {{
        border-color: {C['cyhawk_red']};
        color: {C['text']};
    }}
    
    /* Hero Section */
    .hero-section {{
        margin-bottom: 4rem;
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
        max-width: 600px;
        margin-bottom: 2rem;
    }}
    
    /* Map Container */
    .map-container {{
        background: linear-gradient(135deg, {C['bg_card']} 0%, {C['bg_elevated']} 100%);
        border: 1px solid {C['border']};
        border-radius: 24px;
        padding: 4rem;
        min-height: 650px;
        position: relative;
        overflow: hidden;
        margin-bottom: 2rem;
    }}
    
    /* Map Stats Overlay */
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
    }}
    
    .map-stat-label {{
        font-size: 0.85rem;
        color: {C['text_dim']};
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    /* Legend */
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
    }}
    
    .legend-text {{
        font-size: 0.9rem;
        color: {C['text_dim']};
        font-weight: 500;
    }}
    
    /* Metrics Grid */
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
    
    /* Section Headers */
    .section-header {{
        margin-bottom: 2rem;
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
    
    /* Charts Grid */
    .charts-grid {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 2rem;
        margin-bottom: 4rem;
    }}
    
    .chart-card {{
        background: {C['bg_card']};
        border: 1px solid {C['border']};
        border-radius: 20px;
        padding: 2rem;
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
    
    /* Footer */
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
    
    /* Responsive Design */
    @media (max-width: 1024px) {{
        .metrics-grid {{
            grid-template-columns: repeat(2, 1fr);
        }}
        
        .charts-grid {{
            grid-template-columns: 1fr;
        }}
        
        .map-stats-grid {{
            grid-template-columns: repeat(2, 1fr);
        }}
    }}
    
    @media (max-width: 768px) {{
        .main-header {{
            flex-direction: column;
            gap: 1rem;
            padding: 1rem 1.5rem;
        }}
        
        .header-nav {{
            width: 100%;
            justify-content: space-between;
        }}
        
        .hero-title {{
            font-size: 2.5rem;
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
    }}
    
    /* Plotly chart customization */
    .js-plotly-plot {{
        background: transparent !important;
    }}
    
    /* Remove Streamlit padding */
    .block-container {{
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 1400px;
    }}
</style>
""", unsafe_allow_html=True)

# Header
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
    </div>
</div>
""", unsafe_allow_html=True)

# Theme toggle button (in sidebar for functionality)
with st.sidebar:
    if st.button("🌓 Toggle Theme", key="theme_toggle", use_container_width=True):
        toggle_theme()
        st.rerun()

# Generate sample data
def generate_sample_data():
    """Generate sample threat data"""
    
    # African countries with ISO codes
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
        'Eswatini': 'SWZ', 'Djibouti': 'DJI', 'Reunion': 'REU', 'Comoros': 'COM',
        'Cape Verde': 'CPV', 'Sao Tome and Principe': 'STP', 'Seychelles': 'SYC'
    }
    
    # Generate threat data for countries
    threat_data = []
    for country, iso in countries.items():
        attacks = random.randint(0, 50)
        threat_data.append({
            'country': country,
            'iso_alpha': iso,
            'attacks': attacks
        })
    
    df = pd.DataFrame(threat_data)
    
    # Generate threat actors
    actors = ['LockBit', 'BlackCat', 'Play', 'Cl0p', 'Royal', 'BianLian', 'Medusa', 
              'Akira', 'NoEscape', '8Base', 'Rhysida', 'Hunters International']
    
    actor_data = []
    for actor in actors:
        actor_data.append({
            'actor': actor,
            'attacks': random.randint(10, 80),
            'countries_affected': random.randint(3, 15)
        })
    
    actors_df = pd.DataFrame(actor_data).sort_values('attacks', ascending=False).head(10)
    
    # Generate timeline data
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    timeline_data = []
    for date in dates:
        timeline_data.append({
            'date': date,
            'Ransomware': random.randint(5, 25),
            'Phishing': random.randint(10, 40),
            'DDoS': random.randint(3, 20),
            'Data Breach': random.randint(2, 15)
        })
    
    timeline_df = pd.DataFrame(timeline_data)
    
    # Generate industry data
    industries = ['Financial Services', 'Healthcare', 'Government', 'Energy', 
                  'Telecommunications', 'Education', 'Manufacturing', 'Retail']
    
    industry_data = []
    for industry in industries:
        industry_data.append({
            'industry': industry,
            'attacks': random.randint(20, 100)
        })
    
    industry_df = pd.DataFrame(industry_data).sort_values('attacks', ascending=True)
    
    return df, actors_df, timeline_df, industry_df

# Generate data
map_df, actors_df, timeline_df, industry_df = generate_sample_data()

# Calculate metrics
total_threats = map_df['attacks'].sum()
high_severity = int(total_threats * 0.25)
threat_actors = len(actors_df)
countries_affected = len(map_df[map_df['attacks'] > 0])

# Hero Section
st.markdown(f"""
<div class="hero-section">
    <div class="hero-label">CONTINENTAL INTELLIGENCE</div>
    <h1 class="hero-title">Africa Threat<br>Landscape</h1>
    <p class="hero-subtitle">
        Real-time cyber threat monitoring across 54 African nations with advanced intelligence analytics.
    </p>
</div>
""", unsafe_allow_html=True)

# Africa Map
fig_map = go.Figure()

if not map_df.empty and 'iso_alpha' in map_df.columns:
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
        hovertemplate='<b>%{location}</b><br>Attacks: %{z}<extra></extra>',
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
    paper_bgcolor=C['bg_card'],
    plot_bgcolor=C['bg_card'],
    geo=dict(
        bgcolor=C['bg_card'],
    ),
    font=dict(color=C['text'])
)

st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})

# Map Stats Grid
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
        <div class="map-stat-value">{threat_actors}</div>
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

# Key Metrics
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
        <div class="metric-value">{threat_actors}</div>
        <div class="metric-change">Active Now</div>
    </div>
    
    <div class="metric-card">
        <div class="metric-label">Coverage</div>
        <div class="metric-value">{countries_affected}</div>
        <div class="metric-change">Countries</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Threat Intelligence Section
st.markdown(f"""
<div class="section-header">
    <div class="section-label">ANALYSIS</div>
    <h2 class="section-title">Threat Intelligence</h2>
</div>
""", unsafe_allow_html=True)

# Charts Grid
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="chart-header">
        <h3 class="chart-title">Threat Classification</h3>
        <span class="chart-badge">Live</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Threat Classification Pie Chart
    threat_types = {
        'Ransomware': 180,
        'Phishing': 156,
        'DDoS': 98,
        'Data Breach': 89,
        'Malware': 60
    }
    
    fig_classification = go.Figure(data=[go.Pie(
        labels=list(threat_types.keys()),
        values=list(threat_types.values()),
        hole=0.5,
        marker=dict(
            colors=['#C41E3A', '#FF5722', '#FF9800', '#FFC107', '#FFEB3B'],
            line=dict(color=C['bg'], width=2)
        ),
        textfont=dict(color=C['text'], size=12),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
    )])
    
    fig_classification.update_layout(
        height=280,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor=C['bg_elevated'],
        plot_bgcolor=C['bg_elevated'],
        showlegend=True,
        legend=dict(
            font=dict(color=C['text'], size=10),
            bgcolor=C['bg_elevated'],
            bordercolor=C['border'],
            borderwidth=1
        ),
        font=dict(color=C['text'])
    )
    
    st.plotly_chart(fig_classification, use_container_width=True, config={'displayModeBar': False}, key='chart_classification')

with col2:
    st.markdown(f"""
    <div class="chart-header">
        <h3 class="chart-title">Attack Trends</h3>
        <span class="chart-badge">30 Days</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Attack Trends Timeline
    fig_timeline = go.Figure()
    
    colors_timeline = ['#C41E3A', '#FF9800', '#FFEB3B', '#00E676']
    threat_categories = ['Ransomware', 'Phishing', 'DDoS', 'Data Breach']
    
    for i, category in enumerate(threat_categories):
        fig_timeline.add_trace(go.Scatter(
            x=timeline_df['date'],
            y=timeline_df[category],
            mode='lines',
            name=category,
            line=dict(color=colors_timeline[i], width=2),
            fill='tonexty' if i > 0 else 'tozeroy',
            fillcolor=f'rgba({int(colors_timeline[i][1:3], 16)}, {int(colors_timeline[i][3:5], 16)}, {int(colors_timeline[i][5:7], 16)}, 0.1)',
            hovertemplate='<b>%{fullData.name}</b><br>Date: %{x|%b %d}<br>Attacks: %{y}<extra></extra>'
        ))
    
    fig_timeline.update_layout(
        height=280,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor=C['bg_elevated'],
        plot_bgcolor=C['bg_elevated'],
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
            font=dict(color=C['text'], size=10),
            bgcolor=C['bg_elevated'],
            bordercolor=C['border'],
            borderwidth=1,
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        hovermode='x unified',
        font=dict(color=C['text'])
    )
    
    st.plotly_chart(fig_timeline, use_container_width=True, config={'displayModeBar': False}, key='chart_timeline')

# Second row of charts
col3, col4 = st.columns(2)

with col3:
    st.markdown(f"""
    <div class="chart-header">
        <h3 class="chart-title">Top Threat Actors</h3>
        <span class="chart-badge">Most Active</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Top Threat Actors
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
        height=280,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor=C['bg_elevated'],
        plot_bgcolor=C['bg_elevated'],
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

with col4:
    st.markdown(f"""
    <div class="chart-header">
        <h3 class="chart-title">Targeted Industries</h3>
        <span class="chart-badge">Sector</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Targeted Industries
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
        height=280,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor=C['bg_elevated'],
        plot_bgcolor=C['bg_elevated'],
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

# Ransomware Intelligence Section
st.markdown(f"""
<div class="section-header">
    <div class="section-label">CRITICAL</div>
    <h2 class="section-title">Ransomware Intelligence</h2>
</div>
""", unsafe_allow_html=True)

# Ransomware charts
col5, col6 = st.columns(2)

with col5:
    st.markdown(f"""
    <div class="chart-header">
        <h3 class="chart-title">Active Groups</h3>
        <span class="chart-badge">Critical</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Active Ransomware Groups
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
        height=280,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor=C['bg_elevated'],
        plot_bgcolor=C['bg_elevated'],
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

with col6:
    st.markdown(f"""
    <div class="chart-header">
        <h3 class="chart-title">Impact Assessment</h3>
        <span class="chart-badge">Severity</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Severity Distribution
    severity_data = {
        'Critical': 146,
        'High': 237,
        'Medium': 150,
        'Low': 50
    }
    
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
        height=280,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor=C['bg_elevated'],
        plot_bgcolor=C['bg_elevated'],
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

# Footer
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
    </div>
    <div class="footer-credits">
        © 2025 CyHawk Africa. All Rights Reserved.
    </div>
</div>
""", unsafe_allow_html=True)
