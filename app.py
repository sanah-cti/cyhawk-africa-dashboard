import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
import os
import random
from datetime import timedelta
import base64

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="CyHawk Africa | Threat Intelligence Platform",
    page_icon="assets/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# THEME STATE
# --------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

# --------------------------------------------------
# SOC-GRADE COLORS (Mandiant-inspired)
# --------------------------------------------------
CYHAWK_RED = "#C41E3A"
CYHAWK_RED_DARK = "#9A1529"

def theme_config():
    if st.session_state.theme == "dark":
        return {
            "bg": "#0D1117",
            "bg_secondary": "#161B22",
            "card": "#1C2128",
            "card_hover": "#22272E",
            "border": "#30363D",
            "text": "#E6EDF3",
            "text_secondary": "#8B949E",
            "text_muted": "#6E7681",
            "accent": CYHAWK_RED,
            "success": "#238636",
            "warning": "#9E6A03",
            "danger": "#DA3633",
            "template": "plotly_dark"
        }
    return {
        "bg": "#FFFFFF",
        "bg_secondary": "#F6F8FA",
        "card": "#FFFFFF",
        "card_hover": "#F6F8FA",
        "border": "#D0D7DE",
        "text": "#1F2328",
        "text_secondary": "#636C76",
        "text_muted": "#8C959F",
        "accent": CYHAWK_RED,
        "success": "#1A7F37",
        "warning": "#9A6700",
        "danger": "#D1242F",
        "template": "plotly_white"
    }

C = theme_config()

# --------------------------------------------------
# ENTERPRISE-GRADE CSS
# --------------------------------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-font-smoothing: antialiased;
}}

.main {{
    background-color: {C['bg']};
    padding: 0;
}}

.stApp {{
    background: {C['bg']};
}}

#MainMenu, footer, header {{ visibility: hidden; }}

/* Top Navigation Bar */
.nav-bar {{
    background: {C['card']};
    border-bottom: 1px solid {C['border']};
    padding: 0 2rem;
    margin: -6rem -6rem 0 -6rem;
    height: 70px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}}

.nav-brand {{
    display: flex;
    align-items: center;
    gap: 1rem;
}}

.nav-logo {{
    width: 45px;
    height: 45px;
    border-radius: 8px;
}}

.nav-title {{
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: {C['text']};
    line-height: 1.2;
}}

.nav-subtitle {{
    margin: 0;
    font-size: 0.75rem;
    color: {C['text_muted']};
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 500;
}}

.nav-actions {{
    display: flex;
    gap: 1rem;
    align-items: center;
}}

.status-indicator {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: {C['bg_secondary']};
    border-radius: 6px;
    font-size: 0.875rem;
    color: {C['text_secondary']};
}}

.status-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: {C['success']};
    animation: pulse 2s infinite;
}}

@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.5; }}
}}

/* Content Container */
.content-container {{
    padding: 2rem;
    max-width: 1600px;
    margin: 0 auto;
}}

/* Metric Cards */
.metrics-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}}

.metric-card {{
    background: {C['card']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    padding: 1.5rem;
    transition: all 0.2s ease;
}}

.metric-card:hover {{
    background: {C['card_hover']};
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}}

.metric-label {{
    font-size: 0.875rem;
    font-weight: 500;
    color: {C['text_secondary']};
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.5rem;
}}

.metric-value {{
    font-size: 2.5rem;
    font-weight: 700;
    color: {C['accent']};
    line-height: 1;
    margin-bottom: 0.25rem;
}}

.metric-change {{
    font-size: 0.875rem;
    color: {C['text_muted']};
}}

/* Chart Cards */
.chart-card {{
    background: {C['card']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    transition: border-color 0.2s ease;
}}

.chart-card:hover {{
    border-color: {C['accent']};
}}

.chart-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid {C['border']};
}}

.chart-title {{
    font-size: 1rem;
    font-weight: 600;
    color: {C['text']};
    margin: 0;
}}

.chart-badge {{
    font-size: 0.75rem;
    padding: 0.25rem 0.75rem;
    background: {C['bg_secondary']};
    border-radius: 12px;
    color: {C['text_secondary']};
    font-weight: 500;
}}

/* Sidebar Styling */
[data-testid="stSidebar"] {{
    background: {C['card']};
    border-right: 1px solid {C['border']};
    padding-top: 1rem;
}}

[data-testid="stSidebar"] .stMarkdown {{
    color: {C['text']};
}}

.sidebar-section {{
    background: transparent;
    border: none;
    padding: 0;
    margin-bottom: 1.5rem;
}}

.sidebar-title {{
    font-size: 0.75rem;
    font-weight: 600;
    color: {C['text_muted']};
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid {C['border']};
}}

/* Filter Controls */
.stSelectbox, .stMultiSelect {{
    margin-bottom: 0.75rem;
}}

.stSelectbox label, .stMultiSelect label {{
    font-size: 0.875rem;
    font-weight: 500;
    color: {C['text']};
    margin-bottom: 0.5rem;
}}

/* Buttons */
.stButton > button {{
    background: {C['accent']};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 0.625rem 1.25rem;
    font-weight: 600;
    font-size: 0.875rem;
    transition: all 0.2s ease;
    width: 100%;
}}

.stButton > button:hover {{
    background: {CYHAWK_RED_DARK};
    box-shadow: 0 4px 12px rgba(196, 30, 58, 0.3);
}}

/* Disable chart dragging */
.js-plotly-plot .plotly .modebar {{
    display: none !important;
}}

.js-plotly-plot .plotly .cursor-crosshair {{
    cursor: default !important;
}}

/* Mobile Responsive */
@media (max-width: 768px) {{
    .nav-bar {{
        padding: 0 1rem;
        height: auto;
        min-height: 70px;
        flex-direction: column;
        gap: 1rem;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }}
    
    .metrics-grid {{
        grid-template-columns: 1fr;
    }}
    
    .content-container {{
        padding: 1rem;
    }}
    
    .metric-value {{
        font-size: 2rem;
    }}
    
    .nav-title {{
        font-size: 1rem;
    }}
}}

/* Footer */
.footer {{
    text-align: center;
    color: {C['text_muted']};
    padding: 2rem;
    margin-top: 3rem;
    border-top: 1px solid {C['border']};
    font-size: 0.875rem;
}}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------
def generate_sample_data():
    actors = ['APT28', 'Lazarus Group', 'Anonymous Sudan', 'DarkSide', 'REvil']
    countries = ['Sudan', 'Morocco', 'Nigeria', 'Kenya', 'Egypt', 'South Africa']
    threat_types = ['Ransomware', 'Data Breach', 'Phishing', 'Malware', 'DDoS']
    sectors = ['Government', 'Healthcare', 'Finance', 'Telecommunications', 'Energy']
    severities = ['High', 'Medium', 'Low']
    sources = ['Dark Web', 'Telegram', 'OSINT', 'Partner Feed']
    
    data = []
    start_date = datetime(2025, 1, 1)
    
    for i in range(200):
        date = start_date + timedelta(days=random.randint(0, 350))
        data.append({
            'date': date,
            'actor': random.choice(actors),
            'country': random.choice(countries),
            'threat_type': random.choice(threat_types),
            'sector': random.choice(sectors),
            'severity': random.choice(severities),
            'source': random.choice(sources)
        })
    
    return pd.DataFrame(data)

@st.cache_data
def load_data():
    try:
        csv_path = 'data/incidents.csv'
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df['date'] = pd.to_datetime(df['date'])
        else:
            df = generate_sample_data()
    except:
        df = generate_sample_data()
    
    df['year'] = df['date'].dt.year
    df['month_name'] = df['date'].dt.strftime('%B')
    df['quarter'] = df['date'].dt.quarter
    return df

df = load_data()

# --------------------------------------------------
# NAVIGATION BAR
# --------------------------------------------------
def get_logo_base64():
    logo_path = "assets/cyhawk_logo.png"
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_logo_base64()

col1, col2 = st.columns([3, 1])

with col1:
    if logo_b64:
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="nav-logo">'
    else:
        logo_html = f'<div class="nav-logo" style="background:{C["accent"]};display:flex;align-items:center;justify-content:center;color:white;font-weight:800;font-size:1.5rem;">C</div>'
    
    st.markdown(f"""
    <div class="nav-bar">
        <div class="nav-brand">
            {logo_html}
            <div>
                <div class="nav-title">CyHawk Africa</div>
                <div class="nav-subtitle">Threat Intelligence Platform</div>
            </div>
        </div>
        <div class="nav-actions">
            <div class="status-indicator">
                <div class="status-dot"></div>
                <span>Live Monitoring</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if st.button("🌙" if st.session_state.theme == "dark" else "☀️", key="theme_btn"):
        toggle_theme()
        st.rerun()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-title">TIME PERIOD</div>', unsafe_allow_html=True)
    
    filter_mode = st.selectbox(
        "Filter Mode",
        ["All Data", "Year", "Month", "Quarter"],
        label_visibility="collapsed"
    )
    
    filtered_df = df.copy()
    
    if filter_mode == "Year":
        years = sorted(df['year'].unique(), reverse=True)
        selected_years = st.multiselect("Select Years", options=years, default=years)
        filtered_df = filtered_df[filtered_df['year'].isin(selected_years)]
    
    elif filter_mode == "Month":
        selected_year = st.selectbox("Select Year", options=sorted(df['year'].unique(), reverse=True))
        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        selected_months = st.multiselect("Select Months", options=months, default=months)
        filtered_df = filtered_df[(filtered_df['year'] == selected_year) & (filtered_df['month_name'].isin(selected_months))]
    
    elif filter_mode == "Quarter":
        selected_year = st.selectbox("Select Year", options=sorted(df['year'].unique(), reverse=True))
        quarters = sorted(df[df['year'] == selected_year]['quarter'].unique())
        selected_quarters = st.multiselect("Select Quarters", options=quarters, default=quarters, format_func=lambda x: f"Q{x}")
        filtered_df = filtered_df[(filtered_df['year'] == selected_year) & (filtered_df['quarter'].isin(selected_quarters))]
    
    st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">FILTERS</div>', unsafe_allow_html=True)
    
    selected_threat_types = st.multiselect(
        "Threat Type",
        options=sorted(df['threat_type'].unique()),
        default=df['threat_type'].unique()
    )
    
    selected_severity = st.multiselect(
        "Severity Level",
        options=sorted(df['severity'].unique()),
        default=df['severity'].unique()
    )
    
    selected_sectors = st.multiselect(
        "Industry Sector",
        options=sorted(df['sector'].unique()),
        default=df['sector'].unique()
    )
    
    filtered_df = filtered_df[
        (filtered_df['threat_type'].isin(selected_threat_types)) &
        (filtered_df['severity'].isin(selected_severity)) &
        (filtered_df['sector'].isin(selected_sectors))
    ]
    
    st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">ANALYTICS</div>', unsafe_allow_html=True)
    
    coverage = (len(filtered_df) / len(df)) * 100 if len(df) > 0 else 0
    st.metric("Data Coverage", f"{coverage:.1f}%")
    st.metric("Records Shown", len(filtered_df))

# --------------------------------------------------
# MAIN CONTENT
# --------------------------------------------------
st.markdown('<div class="content-container">', unsafe_allow_html=True)

# Key Metrics
total_threats = len(filtered_df)
high_severity = len(filtered_df[filtered_df['severity'] == 'High'])
active_actors = filtered_df['actor'].nunique()
countries_affected = filtered_df['country'].nunique()

st.markdown(f"""
<div class="metrics-grid">
    <div class="metric-card">
        <div class="metric-label">Total Threats</div>
        <div class="metric-value">{total_threats}</div>
        <div class="metric-change">Across all sources</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">High Severity</div>
        <div class="metric-value">{high_severity}</div>
        <div class="metric-change">Requires immediate attention</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Threat Actors</div>
        <div class="metric-value">{active_actors}</div>
        <div class="metric-change">Unique identifiers</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Countries</div>
        <div class="metric-value">{countries_affected}</div>
        <div class="metric-change">Geographic coverage</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Charts Row 1
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="chart-card">
        <div class="chart-header">
            <h3 class="chart-title">Threat Classification</h3>
            <span class="chart-badge">Distribution</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    threat_counts = filtered_df['threat_type'].value_counts().reset_index()
    threat_counts.columns = ['Threat Type', 'Count']
    
    fig = px.bar(
        threat_counts,
        x='Count',
        y='Threat Type',
        orientation='h',
        template=C["template"],
        color='Count',
        color_continuous_scale=[[0, C['card']], [1, C['accent']]]
    )
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=C['text'], size=12),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        dragmode=False
    )
    fig.update_traces(marker_line_width=0)
    st.plotly_chart(fig, use_container_width=True, key="threat_bar", config={'displayModeBar': False, 'staticPlot': False})

with col2:
    st.markdown(f"""
    <div class="chart-card">
        <div class="chart-header">
            <h3 class="chart-title">Severity Analysis</h3>
            <span class="chart-badge">Risk Levels</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    severity_counts = filtered_df['severity'].value_counts().reset_index()
    severity_counts.columns = ['Severity', 'Count']
    
    color_map = {'High': C['danger'], 'Medium': C['warning'], 'Low': C['success']}
    fig = px.bar(
        severity_counts,
        x='Severity',
        y='Count',
        template=C["template"],
        color='Severity',
        color_discrete_map=color_map
    )
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=C['text'], size=12),
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(showgrid=False, title=""),
        dragmode=False
    )
    st.plotly_chart(fig, use_container_width=True, key="severity_bar", config={'displayModeBar': False})

# Timeline Chart
st.markdown(f"""
<div class="chart-card">
    <div class="chart-header">
        <h3 class="chart-title">Activity Timeline</h3>
        <span class="chart-badge">Daily Aggregation</span>
    </div>
</div>
""", unsafe_allow_html=True)

timeline_df = filtered_df.groupby(filtered_df['date'].dt.date).size().reset_index()
timeline_df.columns = ['Date', 'Count']

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=timeline_df['Date'],
    y=timeline_df['Count'],
    mode="lines",
    fill="tozeroy",
    line=dict(color=C['accent'], width=2),
    fillcolor=f"rgba(196, 30, 58, 0.1)"
))
fig.update_layout(
    height=250,
    margin=dict(l=0, r=0, t=0, b=0),
    template=C["template"],
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color=C['text'], size=12),
    xaxis=dict(showgrid=False, title=""),
    yaxis=dict(showgrid=False, title=""),
    hovermode='x unified',
    dragmode=False
)
st.plotly_chart(fig, use_container_width=True, key="timeline", config={'displayModeBar': False})

# Charts Row 2 - Intelligence Analysis
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="chart-card">
        <div class="chart-header">
            <h3 class="chart-title">Top Threat Actors</h3>
            <span class="chart-badge">Most Active</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    actor_counts = filtered_df['actor'].value_counts().head(10).reset_index()
    actor_counts.columns = ['Actor', 'Count']
    
    fig = px.bar(
        actor_counts,
        x='Count',
        y='Actor',
        orientation='h',
        template=C["template"],
        color='Count',
        color_continuous_scale=[[0, C['card']], [1, C['accent']]]
    )
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=C['text'], size=12),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        dragmode=False
    )
    st.plotly_chart(fig, use_container_width=True, key="actor_bar", config={'displayModeBar': False})

with col2:
    st.markdown(f"""
    <div class="chart-card">
        <div class="chart-header">
            <h3 class="chart-title">Most Targeted Industries</h3>
            <span class="chart-badge">Sector Analysis</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    sector_counts = filtered_df['sector'].value_counts().head(10).reset_index()
    sector_counts.columns = ['Sector', 'Count']
    
    fig = px.bar(
        sector_counts,
        x='Count',
        y='Sector',
        orientation='h',
        template=C["template"],
        color='Count',
        color_continuous_scale=[[0, C['card']], [1, C['accent']]]
    )
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=C['text'], size=12),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        dragmode=False
    )
    st.plotly_chart(fig, use_container_width=True, key="industry_bar", config={'displayModeBar': False})

# Charts Row 3 - Geographic & Threat Analysis
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="chart-card">
        <div class="chart-header">
            <h3 class="chart-title">Top Targeted Countries</h3>
            <span class="chart-badge">Geographic Hotspots</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    country_counts = filtered_df['country'].value_counts().head(10).reset_index()
    country_counts.columns = ['Country', 'Count']
    
    fig = px.bar(
        country_counts,
        x='Count',
        y='Country',
        orientation='h',
        template=C["template"],
        color='Count',
        color_continuous_scale=[[0, C['card']], [1, C['accent']]]
    )
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=C['text'], size=12),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        dragmode=False
    )
    st.plotly_chart(fig, use_container_width=True, key="country_bar", config={'displayModeBar': False})

with col2:
    st.markdown(f"""
    <div class="chart-card">
        <div class="chart-header">
            <h3 class="chart-title">Top Ransomware Groups</h3>
            <span class="chart-badge">Ransomware Activity</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Filter for ransomware threats
    ransomware_df = filtered_df[filtered_df['threat_type'] == 'Ransomware']
    if len(ransomware_df) > 0:
        ransomware_actors = ransomware_df['actor'].value_counts().head(10).reset_index()
        ransomware_actors.columns = ['Group', 'Count']
        
        fig = px.bar(
            ransomware_actors,
            x='Count',
            y='Group',
            orientation='h',
            template=C["template"],
            color='Count',
            color_continuous_scale=[[0, C['card']], [1, C['danger']]]
        )
        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=C['text'], size=12),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
            dragmode=False
        )
        st.plotly_chart(fig, use_container_width=True, key="ransomware_bar", config={'displayModeBar': False})
    else:
        st.info("No ransomware activity in selected period")

# Charts Row 4 - Threat Type Details
st.markdown(f"""
<div class="chart-card">
    <div class="chart-header">
        <h3 class="chart-title">Top Threats</h3>
        <span class="chart-badge">Threat Type Breakdown</span>
    </div>
</div>
""", unsafe_allow_html=True)

threat_details = filtered_df.groupby(['threat_type', 'severity']).size().reset_index(name='count')

fig = px.bar(
    threat_details,
    x='threat_type',
    y='count',
    color='severity',
    template=C["template"],
    color_discrete_map={'High': C['danger'], 'Medium': C['warning'], 'Low': C['success']},
    barmode='stack'
)
fig.update_layout(
    height=300,
    margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color=C['text'], size=12),
    xaxis=dict(showgrid=False, title="Threat Type"),
    yaxis=dict(showgrid=False, title="Count"),
    legend=dict(
        title="Severity",
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    dragmode=False
)
st.plotly_chart(fig, use_container_width=True, key="threats_stacked", config={'displayModeBar': False})

st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# EXPORT (DATA UPLOAD REMOVED - BACKEND ONLY)
# --------------------------------------------------
with st.sidebar:
    st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">EXPORT</div>', unsafe_allow_html=True)
    
    if st.button("Generate Report", use_container_width=True):
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="⬇️ Download CSV",
            data=csv,
            file_name=f"cyhawk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    st.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown(f"""
<div class="footer">
    <strong style="color:{C['accent']}">CyHawk Africa</strong> © {datetime.now().year} | Threat Intelligence Platform<br>
</div>
""", unsafe_allow_html=True)
