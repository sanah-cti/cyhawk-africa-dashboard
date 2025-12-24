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

/* Status Indicators */
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
    box-shadow: 0 0 0 0 rgba(35, 134, 54, 0.7);
}}

@keyframes pulse {{
    0% {{
        box-shadow: 0 0 0 0 rgba(35, 134, 54, 0.7);
    }}
    50% {{
        box-shadow: 0 0 0 8px rgba(35, 134, 54, 0);
    }}
    100% {{
        box-shadow: 0 0 0 0 rgba(35, 134, 54, 0);
    }}
}}

.last-refresh {{
    font-size: 0.75rem;
    color: {C['text_muted']};
    display: flex;
    align-items: center;
    gap: 0.5rem;
}}

.refresh-icon {{
    width: 12px;
    height: 12px;
    border: 2px solid {C['text_muted']};
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 3s linear infinite;
}}

@keyframes spin {{
    0% {{ transform: rotate(0deg); }}
    100% {{ transform: rotate(360deg); }}
}}

.activity-indicator {{
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
}}

.activity-bar {{
    width: 2px;
    height: 12px;
    background: {C['accent']};
    animation: activity 1.5s ease-in-out infinite;
}}

.activity-bar:nth-child(1) {{ animation-delay: 0s; }}
.activity-bar:nth-child(2) {{ animation-delay: 0.2s; }}
.activity-bar:nth-child(3) {{ animation-delay: 0.4s; }}
.activity-bar:nth-child(4) {{ animation-delay: 0.6s; }}

@keyframes activity {{
    0%, 100% {{ height: 6px; opacity: 0.3; }}
    50% {{ height: 16px; opacity: 1; }}
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
    display: flex;
    align-items: center;
    gap: 0.5rem;
}}

.live-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.75rem;
    padding: 0.25rem 0.75rem;
    background: rgba(35, 134, 54, 0.1);
    border: 1px solid {C['success']};
    border-radius: 12px;
    color: {C['success']};
    font-weight: 600;
}}

.live-badge::before {{
    content: '';
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: {C['success']};
    animation: pulse-small 2s infinite;
}}

@keyframes pulse-small {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.3; }}
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
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
            # Drop rows with invalid dates
            df = df.dropna(subset=['date'])
            
            # Fill NaN values in categorical columns with 'Unknown'
            categorical_columns = ['actor', 'country', 'threat_type', 'sector', 'severity', 'source']
            for col in categorical_columns:
                if col in df.columns:
                    df[col] = df[col].fillna('Unknown')
                    # Convert to string to avoid mixed types
                    df[col] = df[col].astype(str)
            
            # If dataframe is empty after cleaning, use sample data
            if len(df) == 0:
                df = generate_sample_data()
        else:
            df = generate_sample_data()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}. Using sample data.")
        df = generate_sample_data()
    
    df['year'] = df['date'].dt.year
    df['month_name'] = df['date'].dt.strftime('%B')
    df['quarter'] = df['date'].dt.quarter
    return df

df = load_data()

# --------------------------------------------------
# NAVIGATION BAR WITH LIVE SIGNALS
# --------------------------------------------------
import time

# Calculate time since last refresh
if 'last_refresh_time' not in st.session_state:
    st.session_state.last_refresh_time = time.time()

current_time = time.time()
minutes_ago = int((current_time - st.session_state.last_refresh_time) / 60)

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
    
    # Get current time for display
    current_time_str = datetime.now().strftime("%H:%M")
    
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
            <div class="status-indicator">
                <div class="activity-indicator">
                    <div class="activity-bar"></div>
                    <div class="activity-bar"></div>
                    <div class="activity-bar"></div>
                    <div class="activity-bar"></div>
                </div>
                <span>{current_time_str} UTC</span>
            </div>
            <div class="last-refresh">
                <div class="refresh-icon"></div>
                <span>Updated {minutes_ago}m ago</span>
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
        options=sorted([t for t in df['threat_type'].unique() if pd.notna(t)]),
        default=list(df['threat_type'].unique())
    )
    
    selected_severity = st.multiselect(
        "Severity Level",
        options=sorted([s for s in df['severity'].unique() if pd.notna(s)]),
        default=list(df['severity'].unique())
    )
    
    selected_sectors = st.multiselect(
        "Industry Sector",
        options=sorted([sec for sec in df['sector'].unique() if pd.notna(sec)]),
        default=list(df['sector'].unique())
    )
    
    filtered_df = filtered_df[
        (filtered_df['threat_type'].isin(selected_threat_types)) &
        (filtered_df['severity'].isin(selected_severity)) &
        (filtered_df['sector'].isin(selected_sectors))
    ]
    
    st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">ANALYTICS</div>', unsafe_allow_html=True)
    
    coverage = (len(filtered_df) / len(df)) * 100 if len(df) > 0 else 0
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Coverage", f"{coverage:.1f}%")
    with col_b:
        st.metric("Records", len(filtered_df))
    
    # Add subtle activity indicator
    st.markdown(f"""
    <div style="margin-top: 1rem; padding: 0.75rem; background: {C['bg_secondary']}; border-radius: 6px; border-left: 3px solid {C['success']};">
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
            <div class="activity-indicator">
                <div class="activity-bar"></div>
                <div class="activity-bar"></div>
                <div class="activity-bar"></div>
            </div>
            <span style="font-size: 0.75rem; color: {C['text_secondary']}; font-weight: 600;">ACTIVE FEED</span>
        </div>
        <div style="font-size: 0.7rem; color: {C['text_muted']};">Intelligence pipeline operational</div>
    </div>
    """, unsafe_allow_html=True)

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
            <span class="live-badge">LIVE</span>
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
            <span class="live-badge">LIVE</span>
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
timeline_df = filtered_df.groupby(filtered_df['date'].dt.date).size().reset_index()
timeline_df.columns = ['Date', 'Count']

# Get time range for display
if len(timeline_df) > 0:
    date_range = f"{timeline_df['Date'].min()} to {timeline_df['Date'].max()}"
else:
    date_range = "No data"

st.markdown(f"""
<div class="chart-card">
    <div class="chart-header">
        <h3 class="chart-title">Activity Timeline</h3>
        <div style="display: flex; gap: 0.5rem; align-items: center;">
            <span class="chart-badge">{date_range}</span>
            <span class="live-badge">STREAMING</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

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

# ============================================================================
# COLORFUL AFRICA THREAT MAP - VIBRANT GRADIENT VERSION
# Replace the fig_map creation section (the go.Figure part) with this
# ============================================================================

with col1:
    st.markdown(f"""
    <div class="chart-card">
        <div class="chart-header">
            <h3 class="chart-title">Africa Threat Map</h3>
            <span class="chart-badge">Hover for Details</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Prepare data: Get top actors for each African country
    african_countries = filtered_df['country'].unique()
    
    map_data = []
    for country in african_countries:
        country_df = filtered_df[filtered_df['country'] == country]
        total_attacks = len(country_df)
        
        # Get top 5 actors targeting this country
        top_actors = country_df['actor'].value_counts().head(5)
        
        # Format actor list for hover text
        actor_list = "<br>".join([
            f"  • {actor}: {count} attack{'s' if count > 1 else ''}" 
            for actor, count in top_actors.items()
        ])
        
        # Get threat type breakdown
        threat_types = country_df['threat_type'].value_counts().head(3)
        threat_list = "<br>".join([
            f"  • {threat}: {count}" 
            for threat, count in threat_types.items()
        ])
        
        map_data.append({
            'Country': country,
            'Attacks': total_attacks,
            'Top_Actors': actor_list if actor_list else '  • No data',
            'Threat_Types': threat_list if threat_list else '  • No data'
        })
    
    map_df = pd.DataFrame(map_data)
    
    # Create detailed hover text
    map_df['hover_text'] = map_df.apply(
        lambda row: (
            f"<b>{row['Country']}</b><br>"
            f"<b>Total Attacks:</b> {row['Attacks']}<br><br>"
            f"<b>Top Threat Actors:</b><br>{row['Top_Actors']}<br><br>"
            f"<b>Primary Threats:</b><br>{row['Threat_Types']}"
        ),
        axis=1
    )
    
    # ISO-3 country codes for African countries
    country_iso_map = {
        'Nigeria': 'NGA', 'South Africa': 'ZAF', 'Kenya': 'KEN', 'Egypt': 'EGY',
        'Ghana': 'GHA', 'Morocco': 'MAR', 'Tanzania': 'TZA', 'Ethiopia': 'ETH',
        'Uganda': 'UGA', 'Algeria': 'DZA', 'Tunisia': 'TUN', 'Zimbabwe': 'ZWE',
        'Mozambique': 'MOZ', 'Zambia': 'ZMB', 'Senegal': 'SEN', 'Rwanda': 'RWA',
        'Cameroon': 'CMR', 'Ivory Coast': 'CIV', "Cote d'Ivoire": 'CIV',
        'Angola': 'AGO', 'Sudan': 'SDN', 'Libya': 'LBY', 'Mali': 'MLI',
        'Malawi': 'MWI', 'Niger': 'NER', 'Somalia': 'SOM', 'Congo': 'COG',
        'Botswana': 'BWA', 'Gabon': 'GAB', 'Mauritius': 'MUS', 'Namibia': 'NAM',
        'Madagascar': 'MDG', 'Burkina Faso': 'BFA', 'Guinea': 'GIN',
        'Benin': 'BEN', 'Burundi': 'BDI', 'Togo': 'TGO', 'Sierra Leone': 'SLE',
        'Liberia': 'LBR', 'Mauritania': 'MRT', 'Eritrea': 'ERI', 'Gambia': 'GMB',
        'Lesotho': 'LSO', 'Equatorial Guinea': 'GNQ', 'Djibouti': 'DJI',
        'Eswatini': 'SWZ', 'Swaziland': 'SWZ', 'Cape Verde': 'CPV',
        'Seychelles': 'SYC', 'Central African Republic': 'CAF', 'Chad': 'TCD',
        'South Sudan': 'SSD', 'Comoros': 'COM', 'Sao Tome and Principe': 'STP',
        'DR Congo': 'COD', 'Democratic Republic of Congo': 'COD'
    }
    
    # Add ISO codes
    map_df['iso_alpha'] = map_df['Country'].map(country_iso_map)
    
    # Remove countries without ISO codes
    map_df = map_df.dropna(subset=['iso_alpha'])
    
    if len(map_df) > 0:
        # COLORFUL GRADIENT - Rainbow spectrum based on attack intensity
        fig_map = go.Figure(data=go.Choropleth(
            locations=map_df['iso_alpha'],
            z=map_df['Attacks'],
            text=map_df['hover_text'],
            hovertemplate='%{text}<extra></extra>',
            
            # 🌈 VIBRANT COLORFUL GRADIENT
            colorscale=[
                [0.0, '#2E7D32'],   # Dark Green (Low attacks)
                [0.15, '#43A047'],  # Green
                [0.25, '#66BB6A'],  # Light Green
                [0.35, '#FDD835'],  # Yellow
                [0.45, '#FFB300'],  # Amber
                [0.55, '#FB8C00'],  # Orange
                [0.65, '#F4511E'],  # Deep Orange
                [0.75, '#E53935'],  # Red
                [0.85, '#C62828'],  # Dark Red
                [1.0, '#880E4F']    # Purple-Red (Highest attacks)
            ],
            
            autocolorscale=False,
            reversescale=False,
            marker_line_color='#212121',
            marker_line_width=0.8,
            
            colorbar=dict(
                title="<b>Attacks</b>",
                thickness=15,
                len=0.7,
                bgcolor='rgba(0,0,0,0)',
                tickfont=dict(color=C['text'], size=11),
                titlefont=dict(color=C['text'], size=12, family="Arial Black"),
                outlinewidth=0
            )
        ))
        
        # Focus on Africa
        fig_map.update_geos(
            scope='africa',
            projection_type='natural earth',
            showframe=False,
            showcoastlines=True,
            coastlinecolor='#37474F',
            coastlinewidth=1,
            showcountries=True,
            countrycolor='#37474F',
            countrywidth=0.5,
            showland=True,
            landcolor=C['bg_secondary'],
            bgcolor=C['bg'],
            showlakes=True,
            lakecolor=C['bg'],
            showocean=True,
            oceancolor=C['bg']
        )
        
        fig_map.update_layout(
            height=450,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            geo=dict(
                bgcolor='rgba(0,0,0,0)',
                lakecolor='rgba(0,0,0,0)'
            ),
            font=dict(color=C['text'], size=11),
            dragmode=False,
            hoverlabel=dict(
                bgcolor='#212121',
                font_size=12,
                font_color='white',
                font_family="Arial",
                bordercolor='#FDD835'
            )
        )
        
        st.plotly_chart(fig_map, use_container_width=True, key="africa_map", config={'displayModeBar': False})
        
        # Colorful legend with gradient explanation
        st.markdown(f"""
        <div style="
            padding: 1rem;
            background: linear-gradient(135deg, {C['card']} 0%, {C['bg_secondary']} 100%);
            border-radius: 8px;
            border: 1px solid {C['border']};
            margin-top: 0.5rem;
        ">
            <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
                <div style="flex: 1; min-width: 200px;">
                    <p style="margin: 0; color: {C['text']}; font-size: 0.9rem; font-weight: 600;">
                        💡 Hover over countries for detailed threat intelligence
                    </p>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="color: {C['text_secondary']}; font-size: 0.85rem;">Color Guide:</span>
                    <div style="display: flex; align-items: center; gap: 0.25rem;">
                        <div style="width: 20px; height: 20px; background: #2E7D32; border-radius: 3px;"></div>
                        <span style="color: {C['text_muted']}; font-size: 0.75rem;">Low</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.25rem;">
                        <div style="width: 20px; height: 20px; background: #FDD835; border-radius: 3px;"></div>
                        <span style="color: {C['text_muted']}; font-size: 0.75rem;">Medium</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.25rem;">
                        <div style="width: 20px; height: 20px; background: #F4511E; border-radius: 3px;"></div>
                        <span style="color: {C['text_muted']}; font-size: 0.75rem;">High</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.25rem;">
                        <div style="width: 20px; height: 20px; background: #880E4F; border-radius: 3px;"></div>
                        <span style="color: {C['text_muted']}; font-size: 0.75rem;">Critical</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No African country data available in current filter selection")
        threat_list = "<br>".join([
            f"  • {threat}: {count}" 
            for threat, count in threat_types.items()
        ])
        
        map_data.append({
            'Country': country,
            'Attacks': total_attacks,
            'Top_Actors': actor_list if actor_list else '  • No data',
            'Threat_Types': threat_list if threat_list else '  • No data'
        })
    
    map_df = pd.DataFrame(map_data)
    
    # Create detailed hover text
    map_df['hover_text'] = map_df.apply(
        lambda row: (
            f"<b>{row['Country']}</b><br>"
            f"<b>Total Attacks:</b> {row['Attacks']}<br><br>"
            f"<b>Top Threat Actors:</b><br>{row['Top_Actors']}<br><br>"
            f"<b>Primary Threats:</b><br>{row['Threat_Types']}"
        ),
        axis=1
    )
    
    # ISO-3 country codes for African countries
    country_iso_map = {
        'Nigeria': 'NGA', 'South Africa': 'ZAF', 'Kenya': 'KEN', 'Egypt': 'EGY',
        'Ghana': 'GHA', 'Morocco': 'MAR', 'Tanzania': 'TZA', 'Ethiopia': 'ETH',
        'Uganda': 'UGA', 'Algeria': 'DZA', 'Tunisia': 'TUN', 'Zimbabwe': 'ZWE',
        'Mozambique': 'MOZ', 'Zambia': 'ZMB', 'Senegal': 'SEN', 'Rwanda': 'RWA',
        'Cameroon': 'CMR', 'Ivory Coast': 'CIV', "Cote d'Ivoire": 'CIV',
        'Angola': 'AGO', 'Sudan': 'SDN', 'Libya': 'LBY', 'Mali': 'MLI',
        'Malawi': 'MWI', 'Niger': 'NER', 'Somalia': 'SOM', 'Congo': 'COG',
        'Botswana': 'BWA', 'Gabon': 'GAB', 'Mauritius': 'MUS', 'Namibia': 'NAM',
        'Madagascar': 'MDG', 'Burkina Faso': 'BFA', 'Guinea': 'GIN',
        'Benin': 'BEN', 'Burundi': 'BDI', 'Togo': 'TGO', 'Sierra Leone': 'SLE',
        'Liberia': 'LBR', 'Mauritania': 'MRT', 'Eritrea': 'ERI', 'Gambia': 'GMB',
        'Lesotho': 'LSO', 'Equatorial Guinea': 'GNQ', 'Djibouti': 'DJI',
        'Eswatini': 'SWZ', 'Swaziland': 'SWZ', 'Cape Verde': 'CPV',
        'Seychelles': 'SYC', 'Central African Republic': 'CAF', 'Chad': 'TCD',
        'South Sudan': 'SSD', 'Comoros': 'COM', 'Sao Tome and Principe': 'STP',
        'DR Congo': 'COD', 'Democratic Republic of Congo': 'COD'
    }
    
    # Add ISO codes
    map_df['iso_alpha'] = map_df['Country'].map(country_iso_map)
    
    # Remove countries without ISO codes (non-African or unrecognized)
    map_df = map_df.dropna(subset=['iso_alpha'])
    
    if len(map_df) > 0:
        # Create the Africa choropleth map
        fig_map = go.Figure(data=go.Choropleth(
            locations=map_df['iso_alpha'],
            z=map_df['Attacks'],
            text=map_df['hover_text'],
            hovertemplate='%{text}<extra></extra>',
            colorscale=[
                [0, C['card']],
                [0.3, '#8B1538'],
                [0.6, C['accent']],
                [1.0, '#FF6B8A']
            ],
            autocolorscale=False,
            reversescale=False,
            marker_line_color=C['border'],
            marker_line_width=0.5,
            colorbar=dict(
                title="Attacks",
                thickness=10,
                len=0.7,
                bgcolor='rgba(0,0,0,0)',
                tickfont=dict(color=C['text'], size=10),
                titlefont=dict(color=C['text'], size=11)
            )
        ))
        
        # Focus on Africa
        fig_map.update_geos(
            scope='africa',
            projection_type='natural earth',
            showframe=False,
            showcoastlines=True,
            coastlinecolor=C['border'],
            showcountries=True,
            countrycolor=C['border'],
            showland=True,
            landcolor=C['card'],
            bgcolor=C['bg'],
            showlakes=False,
            showocean=True,
            oceancolor=C['bg_secondary']
        )
        
        fig_map.update_layout(
            height=450,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            geo=dict(
                bgcolor='rgba(0,0,0,0)',
                lakecolor='rgba(0,0,0,0)'
            ),
            font=dict(color=C['text'], size=11),
            dragmode=False,
            hoverlabel=dict(
                bgcolor=C['card'],
                font_size=12,
                font_color=C['text'],
                bordercolor=C['accent']
            )
        )
        
        st.plotly_chart(fig_map, use_container_width=True, key="africa_map", config={'displayModeBar': False})
        
        # Add helpful legend below map
        st.markdown(f"""
        <div style="
            padding: 0.75rem;
            background: {C['card']};
            border-radius: 8px;
            border-left: 3px solid {C['accent']};
            margin-top: 0.5rem;
        ">
            <p style="margin: 0; color: {C['text_secondary']}; font-size: 0.85rem;">
                💡 <b>Hover over countries</b> to see top 5 threat actors and primary attack types
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No African country data available in current filter selection")

# The rest of your code continues here (col2 with Top Ransomware Groups, etc.)

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
# FOOTER WITH SYSTEM STATUS
# --------------------------------------------------
# Calculate uptime (simulated)
uptime_hours = int((time.time() - st.session_state.last_refresh_time) / 3600)
if uptime_hours == 0:
    uptime_display = f"{int((time.time() - st.session_state.last_refresh_time) / 60)} minutes"
else:
    uptime_display = f"{uptime_hours}h {int(((time.time() - st.session_state.last_refresh_time) % 3600) / 60)}m"

st.markdown(f"""
<div class="footer">
    <div style="display: flex; justify-content: center; gap: 2rem; margin-bottom: 1rem; flex-wrap: wrap;">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <div style="width: 8px; height: 8px; border-radius: 50%; background: {C['success']};"></div>
            <span style="font-size: 0.75rem; color: {C['text_secondary']};">System Operational</span>
        </div>
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <div class="refresh-icon"></div>
            <span style="font-size: 0.75rem; color: {C['text_secondary']};">Last sync: {minutes_ago}m ago</span>
        </div>
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 0.75rem; color: {C['text_secondary']};">⏱ Uptime: {uptime_display}</span>
        </div>
    </div>
    <strong style="color:{C['accent']}">CyHawk Africa</strong> © {datetime.now().year} | Threat Intelligence Platform<br>
    <small style="color:{C['text_muted']}">Cyber Intelligence for Africa</small>
</div>
""", unsafe_allow_html=True)
