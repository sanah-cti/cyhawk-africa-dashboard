import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
import random
import os

# Check for plotly installation
PLOTLY_AVAILABLE = False
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    st.error("❌ Plotly is not installed. Please run: `pip install plotly`")
    st.stop()

# Check for matplotlib installation
MATPLOTLIB_AVAILABLE = False
try:
    from matplotlib.backends.backend_pdf import PdfPages
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    st.warning("⚠️ Matplotlib not available. PDF reports will be disabled.")

# Page configuration
st.set_page_config(
    page_title="CyHawk Africa - CTI Dashboard",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme in session state
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# Theme toggle function
def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# CyHawk Brand Colors
BRAND_RED = '#DC143C'
BRAND_WHITE = '#FFFFFF'
DARK_BG = '#0a0e27'
DARK_CARD = '#141b3d'
DARK_BORDER = '#1e2847'

# Theme configurations
def get_theme_colors():
    if st.session_state.theme == 'dark':
        return {
            'bg_primary': DARK_BG,
            'bg_secondary': '#0f1429',
            'bg_card': DARK_CARD,
            'text_primary': BRAND_WHITE,
            'text_secondary': '#8b92b8',
            'accent': BRAND_RED,
            'accent_light': '#ff4458',
            'border': DARK_BORDER,
            'success': '#00ff88',
            'warning': '#ffc107',
            'chart_bg': 'rgba(0,0,0,0)',
            'plotly_template': 'plotly_dark'
        }
    else:
        return {
            'bg_primary': '#f5f7fa',
            'bg_secondary': '#ffffff',
            'bg_card': '#ffffff',
            'text_primary': '#1a1d29',
            'text_secondary': '#6b7280',
            'accent': BRAND_RED,
            'accent_light': '#ff4458',
            'border': '#e5e7eb',
            'success': '#00d084',
            'warning': '#f59e0b',
            'chart_bg': 'rgba(255,255,255,0)',
            'plotly_template': 'plotly_white'
        }

colors = get_theme_colors()

# Custom CSS with CyHawk branding
css_styles = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {{
        font-family: 'Inter', sans-serif;
    }}
    
    .main {{
        background-color: {colors['bg_primary']};
    }}
    
    .stApp {{
        background: {colors['bg_primary']};
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Top Header Bar */
    .top-header {{
        background: {colors['bg_card']};
        padding: 1.5rem 2rem;
        border-bottom: 1px solid {colors['border']};
        margin: -6rem -6rem 2rem -6rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    
    .brand-section {{
        display: flex;
        align-items: center;
        gap: 1rem;
    }}
    
    .brand-logo {{
        font-size: 2rem;
        color: {colors['accent']};
        font-weight: 800;
    }}
    
    .brand-title {{
        color: {colors['text_primary']};
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
    }}
    
    .brand-subtitle {{
        color: {colors['text_secondary']};
        font-size: 0.85rem;
        margin: 0;
        font-weight: 400;
    }}
    
    /* Stats Bar */
    .stats-bar {{
        display: flex;
        gap: 2rem;
        align-items: center;
    }}
    
    .stat-item {{
        text-align: center;
    }}
    
    .stat-value {{
        font-size: 1.8rem;
        font-weight: 700;
        color: {colors['accent']};
        line-height: 1;
        margin: 0;
    }}
    
    .stat-label {{
        font-size: 0.7rem;
        color: {colors['text_secondary']};
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.25rem;
    }}
    
    /* Status Indicators */
    .status-bar {{
        background: {colors['bg_card']};
        border: 1px solid {colors['border']};
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin-bottom: 1.5rem;
        display: flex;
        gap: 2rem;
        align-items: center;
    }}
    
    .status-item {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.9rem;
    }}
    
    .status-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: {colors['success']};
        animation: pulse 2s infinite;
    }}
    
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
    }}
    
    .status-warning {{
        background: {colors['warning']};
    }}
    
    /* Section Cards */
    .section-card {{
        background: {colors['bg_card']};
        border: 1px solid {colors['border']};
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }}
    
    .section-header {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.5rem;
    }}
    
    .section-icon {{
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, {colors['accent']} 0%, {colors['accent_light']} 100%);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
    }}
    
    .section-title {{
        color: {colors['text_primary']};
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0;
    }}
    
    /* Tabs Navigation */
    .nav-tabs {{
        display: flex;
        gap: 0.5rem;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid {colors['border']};
    }}
    
    .nav-tab {{
        padding: 0.5rem 1.5rem;
        color: {colors['text_secondary']};
        text-decoration: none;
        font-weight: 500;
        border-radius: 6px;
        transition: all 0.3s;
        cursor: pointer;
    }}
    
    .nav-tab.active {{
        color: {colors['accent']};
        background: rgba(220, 20, 60, 0.1);
    }}
    
    .nav-tab:hover {{
        color: {colors['accent']};
        background: rgba(220, 20, 60, 0.05);
    }}
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background-color: {colors['bg_secondary']};
        border-right: 1px solid {colors['border']};
    }}
    
    [data-testid="stSidebar"] .stMarkdown {{
        color: {colors['text_primary']};
    }}
    
    /* Filter sections */
    .filter-group {{
        background: {colors['bg_card']};
        border: 1px solid {colors['border']};
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }}
    
    .filter-title {{
        color: {colors['text_primary']};
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    /* Buttons */
    .stButton > button {{
        background: linear-gradient(135deg, {colors['accent']} 0%, {colors['accent_light']} 100%);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s;
        width: 100%;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(220, 20, 60, 0.3);
    }}
    
    /* Theme toggle */
    .theme-toggle {{
        background: {colors['bg_card']};
        border: 1px solid {colors['border']};
        border-radius: 6px;
        padding: 0.5rem 1rem;
        cursor: pointer;
        color: {colors['text_primary']};
        font-size: 1.2rem;
        transition: all 0.3s;
    }}
    
    .theme-toggle:hover {{
        background: {colors['accent']};
        color: white;
    }}
    
    /* Metrics styling */
    [data-testid="metric-container"] {{
        background: {colors['bg_card']};
        border: 1px solid {colors['border']};
        border-radius: 8px;
        padding: 1rem;
    }}
    
    </style>
"""
st.markdown(css_styles, unsafe_allow_html=True)

# Generate sample data function
def generate_sample_data():
    """Generate sample threat intelligence data"""
    actors = ['ifalcon', 'Keymous Plus', 'APT28', 'Lazarus Group', 'Anonymous Sudan', 'DarkSide', 'REvil']
    countries = ['Sudan', 'Morocco', 'Nigeria', 'Kenya', 'Egypt', 'South Africa', 'Ghana', 'Ethiopia']
    threat_types = ['DDOS', 'Data Breach', 'Ransomware', 'Phishing', 'Malware', 'Initial Access', 'SQL Injection']
    sectors = ['Government', 'Health', 'Agriculture', 'Telecommunications', 'Finance', 'Energy', 'Education', 'Transportation']
    severities = ['High', 'Medium', 'Low']
    sources = ['Dark Web', 'Telegram', 'Twitter', 'Forums', 'Email', 'OSINT']
    
    data = []
    start_date = datetime(2025, 1, 1)
    
    for i in range(150):
        date = start_date + timedelta(days=random.randint(0, 300))
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'actor': random.choice(actors),
            'country': random.choice(countries),
            'threat_type': random.choice(threat_types),
            'sector': random.choice(sectors),
            'severity': random.choice(severities),
            'source': random.choice(sources)
        })
    
    return pd.DataFrame(data)

# Load data with comprehensive error handling
@st.cache_data(ttl=300)
def load_data():
    """Load threat intelligence data with error handling"""
    try:
        csv_path = 'data/incidents.csv'
        
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            required_columns = ['date', 'actor', 'country', 'threat_type', 'sector', 'severity', 'source']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.warning(f"⚠️ CSV file is missing columns: {', '.join(missing_columns)}. Using sample data.")
                df = generate_sample_data()
            else:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                invalid_dates = df['date'].isna().sum()
                if invalid_dates > 0:
                    st.warning(f"⚠️ Found {invalid_dates} rows with invalid dates. They will be excluded.")
                    df = df.dropna(subset=['date'])
                
                if len(df) == 0:
                    st.error("❌ No valid data found in CSV. Using sample data.")
                    df = generate_sample_data()
                    df['date'] = pd.to_datetime(df['date'])
        else:
            df = generate_sample_data()
            df['date'] = pd.to_datetime(df['date'])
        
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['month_name'] = df['date'].dt.strftime('%B')
        df['quarter'] = df['date'].dt.quarter
        df['day_of_week'] = df['date'].dt.day_name()
        
        return df
        
    except Exception as e:
        st.error(f"❌ Unexpected error loading data: {str(e)}. Using sample data.")
        df = generate_sample_data()
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['month_name'] = df['date'].dt.strftime('%B')
        df['quarter'] = df['date'].dt.quarter
        df['day_of_week'] = df['date'].dt.day_name()
        return df

# Load data
with st.spinner("Loading threat intelligence data..."):
    try:
        df = load_data()
    except Exception as e:
        st.error(f"Critical error: {str(e)}")
        st.stop()

# Top Header
col1, col2 = st.columns([3, 1])
with col1:
    header_html = f"""
        <div class="top-header">
            <div class="brand-section">
                <div class="brand-logo">🦅</div>
                <div>
                    <h1 class="brand-title">CyHawk Africa</h1>
                    <p class="brand-subtitle">Real-Time Threat Intelligence</p>
                </div>
            </div>
            <div class="stats-bar">
                <div class="stat-item">
                    <div class="stat-value">{len(df)}</div>
                    <div class="stat-label">Total Threats</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{df['actor'].nunique()}</div>
                    <div class="stat-label">Active Actors</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{len(df[df['severity'] == 'High'])}</div>
                    <div class="stat-label">High Severity</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{df['country'].nunique()}</div>
                    <div class="stat-label">Countries</div>
                </div>
            </div>
        </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

with col2:
    theme_icon = "🌙" if st.session_state.theme == 'dark' else "☀️"
    if st.button(theme_icon, key="theme_toggle"):
        toggle_theme()
        st.rerun()

# Sidebar filters
with st.sidebar:
    st.markdown('<div class="filter-group">', unsafe_allow_html=True)
    st.markdown('<div class="filter-title">⏱ Time Filter</div>', unsafe_allow_html=True)
    
    filter_mode = st.radio(
        "",
        ["Date Range", "Year", "Month", "Quarter", "Daily"],
        index=0,
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    filtered_df = df.copy()
    
    # Apply date filters
    try:
        if filter_mode == "Date Range":
            min_date = df['date'].min().date()
            max_date = df['date'].max().date()
            date_range = st.date_input(
                "Select Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            if len(date_range) == 2:
                filtered_df = filtered_df[
                    (filtered_df['date'].dt.date >= date_range[0]) &
                    (filtered_df['date'].dt.date <= date_range[1])
                ]
        
        elif filter_mode == "Year":
            years = sorted(df['year'].unique(), reverse=True)
            selected_years = st.multiselect("Select Year(s)", options=years, default=years)
            filtered_df = filtered_df[filtered_df['year'].isin(selected_years)]
        
        elif filter_mode == "Month":
            selected_year = st.selectbox("Year", options=sorted(df['year'].unique(), reverse=True))
            months = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
            available_months = df[df['year'] == selected_year]['month_name'].unique()
            default_months = [m for m in months if m in available_months]
            selected_months = st.multiselect("Month(s)", options=months, default=default_months)
            filtered_df = filtered_df[
                (filtered_df['year'] == selected_year) &
                (filtered_df['month_name'].isin(selected_months))
            ]
        
        elif filter_mode == "Quarter":
            selected_year = st.selectbox("Year", options=sorted(df['year'].unique(), reverse=True))
            quarters = sorted(df[df['year'] == selected_year]['quarter'].unique())
            selected_quarters = st.multiselect(
                "Quarter(s)",
                options=quarters,
                default=quarters,
                format_func=lambda x: f"Q{x}"
            )
            filtered_df = filtered_df[
                (filtered_df['year'] == selected_year) &
                (filtered_df['quarter'].isin(selected_quarters))
            ]
        
        elif filter_mode == "Daily":
            selected_date = st.date_input(
                "Date",
                value=df['date'].max().date(),
                min_value=df['date'].min().date(),
                max_value=df['date'].max().date()
            )
            filtered_df = filtered_df[filtered_df['date'].dt.date == selected_date]
    
    except Exception as e:
        st.error(f"Error applying date filters: {str(e)}")
        filtered_df = df.copy()
    
    # Additional filters
    try:
        st.markdown('<div class="filter-group">', unsafe_allow_html=True)
        st.markdown('<div class="filter-title">🎯 Category Filters</div>', unsafe_allow_html=True)
        
        selected_threat_types = st.multiselect(
            "Threat Type",
            options=sorted(df['threat_type'].unique()),
            default=df['threat_type'].unique()
        )
        
        selected_severity = st.multiselect(
            "Severity",
            options=sorted(df['severity'].unique()),
            default=df['severity'].unique()
        )
        
        selected_sectors = st.multiselect(
            "Sector",
            options=sorted(df['sector'].unique()),
            default=df['sector'].unique()
        )
        
        selected_actors = st.multiselect(
            "Threat Actor",
            options=sorted(df['actor'].unique()),
            default=df['actor'].unique()
        )
        
        selected_countries = st.multiselect(
            "Country",
            options=sorted(df['country'].unique()),
            default=df['country'].unique()
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Apply filters
        filtered_df = filtered_df[
            (filtered_df['threat_type'].isin(selected_threat_types)) &
            (filtered_df['sector'].isin(selected_sectors)) &
            (filtered_df['actor'].isin(selected_actors)) &
            (filtered_df['severity'].isin(selected_severity)) &
            (filtered_df['country'].isin(selected_countries))
        ]
    
    except Exception as e:
        st.error(f"Error applying filters: {str(e)}")
    
    # Statistics
    st.markdown('<div class="filter-group">', unsafe_allow_html=True)
    st.markdown('<div class="filter-title">📊 Statistics</div>', unsafe_allow_html=True)
    st.metric("Filtered Records", len(filtered_df))
    if len(df) > 0 and len(filtered_df) > 0:
        coverage = (len(filtered_df) / len(df)) * 100
        st.metric("Coverage", f"{coverage:.1f}%")
    st.markdown('</div>', unsafe_allow_html=True)

# Check if filtered data is empty
if len(filtered_df) == 0:
    st.warning("⚠️ No data matches your current filters.")
    st.stop()

# Status Bar
current_time = datetime.now().strftime("%I:%M %p")
status_html = f"""
    <div class="status-bar">
        <div class="status-item">
            <div class="status-dot"></div>
            <span style="color: {colors['success']}; font-weight: 600;">Feed Connected</span>
        </div>
        <div class="status-item">
            <div class="status-dot status-warning"></div>
            <span style="color: {colors['text_secondary']};">Charts updating...</span>
        </div>
        <div class="status-item">
            <div class="status-dot"></div>
            <span style="color: {colors['text_secondary']};">Last alert: 4 minutes ago</span>
        </div>
    </div>
"""
st.markdown(status_html, unsafe_allow_html=True)

# Tabs Navigation
tabs_html = """
    <div class="nav-tabs">
        <div class="nav-tab active">Overview</div>
        <div class="nav-tab">Live Feed</div>
        <div class="nav-tab">Timeline</div>
        <div class="nav-tab">Geolocation</div>
        <div class="nav-tab">Activity Heatmap</div>
        <div class="nav-tab">Analytics</div>
    </div>
"""
st.markdown(tabs_html, unsafe_allow_html=True)

# Charts Row 1
col1, col2 = st.columns(2)

try:
    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        header_html = """
            <div class="section-header">
                <div class="section-icon">📊</div>
                <h3 class="section-title">Threat Distribution</h3>
            </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)
        
        threat_counts = filtered_df['threat_type'].value_counts().reset_index()
        threat_counts.columns = ['Threat Type', 'Count']
        
        fig_threat = px.pie(
            threat_counts,
            values='Count',
            names='Threat Type',
            hole=0.5,
            template=colors['plotly_template'],
            color_discrete_sequence=px.colors.sequential.Reds
        )
        fig_threat.update_layout(
            paper_bgcolor=colors['chart_bg'],
            plot_bgcolor=colors['chart_bg'],
            font=dict(color=colors['text_primary'], size=11),
            height=350,
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.1, font=dict(size=10))
        )
        fig_threat.update_traces(textposition='inside', textinfo='percent', textfont_size=12)
        st.plotly_chart(fig_threat, width='stretch', key="threat_dist")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        header_html = """
            <div class="section-header">
                <div class="section-icon">⚠️</div>
                <h3 class="section-title">Severity Breakdown</h3>
            </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)
        
        severity_counts = filtered_df['severity'].value_counts().reset_index()
        severity_counts.columns = ['Severity', 'Count']
        
        color_map = {'High': BRAND_RED, 'Medium': '#ffc107', 'Low': '#00ff88'}
        
        fig_severity = px.bar(
            severity_counts,
            x='Severity',
            y='Count',
            text='Count',
            template=colors['plotly_template'],
            color='Severity',
            color_discrete_map=color_map
        )
        fig_severity.update_traces(textposition='outside', textfont=dict(size=14, color=colors['text_primary']))
        fig_severity.update_layout(
            paper_bgcolor=colors['chart_bg'],
            plot_bgcolor=colors['chart_bg'],
            font=dict(color=colors['text_primary']),
            height=350,
            showlegend=False,
            xaxis_title="",
            yaxis_title="Count",
            yaxis=dict(showgrid=True, gridcolor=colors['border'])
        )
        st.plotly_chart(fig_severity, width='stretch', key="severity_breakdown")
        st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error creating charts: {str(e)}")

# Daily Trends Chart
try:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    header_html = """
        <div class="section-header">
            <div class="section-icon">📈</div>
            <h3 class="section-title">Daily Trends</h3>
        </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
    
    timeline_df = filtered_df.groupby(filtered_df['date'].dt.date).size().reset_index()
    timeline_df.columns = ['Date', 'Alerts']
    
    fig_timeline = go.Figure()
    fig_timeline.add_trace(go.Scatter(
        x=timeline_df['Date'],
        y=timeline_df['Alerts'],
        mode='lines',
        line=dict(color='#00d4ff', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 212, 255, 0.2)',
        name='Alerts'
    ))
    
    fig_timeline.update_layout(
        paper_bgcolor=colors['chart_bg'],
        plot_bgcolor=colors['chart_bg'],
        font=dict(color=colors['text_primary']),
        height=300,
        xaxis=dict(
            title="",
            showgrid=True,
            gridcolor=colors['border'],
            tickangle=-45
        ),
        yaxis=dict(
            title="",
            showgrid=True,
            gridcolor=colors['border']
        ),
        hovermode='x unified',
        template=colors['plotly_template'],
        margin=dict(l=40, r=20, t=20, b=60)
    )
    st.plotly_chart(fig_timeline, width='stretch', key="daily_trends")
    st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error creating timeline: {str(e)}")

# Additional Charts Row
col1, col2 = st.columns(2)

try:
    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        header_html = """
            <div class="section-header">
                <div class="section-icon">🌍</div>
                <h3 class="section-title">Geographic Distribution</h3>
            </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)
        
        country_counts = filtered_df['country'].value_counts().head(10).reset_index()
        country_counts.columns = ['Country', 'Count']
        
        fig_geo = px.bar(
            country_counts,
            y='Country',
            x='Count',
            orientation='h',
            text='Count',
            template=colors['plotly_template'],
            color='Count',
            color_continuous_scale=[[0, '#141b3d'], [1, BRAND_RED]]
        )
        fig_geo.update_traces(textposition='outside', textfont=dict(color=colors['text_primary']))
        fig_geo.update_layout(
            paper_bgcolor=colors['chart_bg'],
            plot_bgcolor=colors['chart_bg'],
            font=dict(color=colors['text_primary']),
            height=350,
            showlegend=False,
            xaxis_title="",
            yaxis_title="",
            xaxis=dict(showgrid=True, gridcolor=colors['border'])
        )
        st.plotly_chart(fig_geo, width='stretch', key="geo_dist")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(f"""
            <div class="section-header">
                <div class="section-icon">🎯</div>
                <h3 class="
