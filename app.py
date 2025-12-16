import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
import os
import random
from datetime import timedelta

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="CyHawk Africa – Cyber Threat Intelligence",
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
# BRAND COLORS
# --------------------------------------------------
BRAND_RED = "#B91C1C"
DARK_BG = "#0a0e27"
DARK_CARD = "#141b3d"
DARK_BORDER = "#1e2847"

def theme():
    if st.session_state.theme == "dark":
        return {
            "bg": DARK_BG,
            "card": DARK_CARD,
            "border": DARK_BORDER,
            "text": "#FFFFFF",
            "muted": "#9aa3c7",
            "template": "plotly_dark"
        }
    return {
        "bg": "#f5f7fa",
        "card": "#ffffff",
        "border": "#e5e7eb",
        "text": "#111827",
        "muted": "#6b7280",
        "template": "plotly_white"
    }

C = theme()

# --------------------------------------------------
# CSS
# --------------------------------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* {{ font-family: 'Inter', sans-serif; }}
.main {{ background-color: {C['bg']}; }}
.stApp {{ background: {C['bg']}; }}
#MainMenu, footer, header {{ visibility: hidden; }}

.top-header {{
    background: {C['card']};
    border-bottom: 1px solid {C['border']};
    padding: 1.5rem 2rem;
    margin: -6rem -6rem 2rem -6rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.section-card {{
    background: {C['card']};
    border: 1px solid {C['border']};
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}}

.stat-box {{
    text-align: center;
}}

.stat-value {{
    font-size: 2rem;
    font-weight: 700;
    color: {BRAND_RED};
    margin: 0;
}}

.stat-label {{
    font-size: 0.75rem;
    color: {C['muted']};
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

.brand-logo {{
    width: 55px;
    height: 55px;
    background: {BRAND_RED};
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.8rem;
    color: white;
    font-weight: 800;
    border: 2px solid white;
}}

[data-testid="stSidebar"] {{
    background-color: {C['card']};
    border-right: 1px solid {C['border']};
}}

.filter-group {{
    background: {C['card']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
}}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------
def generate_sample_data():
    actors = ['APT28', 'Lazarus Group', 'Anonymous Sudan', 'DarkSide', 'REvil', 'ifalcon', 'Keymous Plus']
    countries = ['Sudan', 'Morocco', 'Nigeria', 'Kenya', 'Egypt', 'South Africa', 'Ghana', 'Ethiopia']
    threat_types = ['DDOS', 'Data Breach', 'Ransomware', 'Phishing', 'Malware', 'Initial Access']
    sectors = ['Government', 'Health', 'Agriculture', 'Telecommunications', 'Finance', 'Energy', 'Education']
    severities = ['High', 'Medium', 'Low']
    sources = ['Dark Web', 'Telegram', 'Twitter', 'Forums', 'OSINT']
    
    data = []
    start_date = datetime(2025, 1, 1)
    
    for i in range(150):
        date = start_date + timedelta(days=random.randint(0, 300))
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
# HEADER
# --------------------------------------------------
col1, col2 = st.columns([3, 1])

with col1:
    total_threats = len(df)
    active_actors = df['actor'].nunique()
    high_severity = len(df[df['severity'] == 'High'])
    countries = df['country'].nunique()
    
    # Check if logo exists
    logo_path = "assets/cyhawk_logo.png"
    if os.path.exists(logo_path):
        logo_html = f'<img src="app/static/{logo_path}" style="width:55px;height:55px;border-radius:50%;border:2px solid white;">'
    else:
        logo_html = '<div class="brand-logo">C</div>'
    
    st.markdown(f"""
    <div class="top-header">
        <div style="display:flex;align-items:center;gap:1rem">
            {logo_html}
            <div>
                <h2 style="margin:0;color:{C['text']}">CyHawk Africa</h2>
                <p style="margin:0;color:{C['muted']};font-size:0.9rem">Real-Time Threat Intelligence</p>
            </div>
        </div>
        <div style="display:flex;gap:2rem">
            <div class="stat-box">
                <div class="stat-value">{total_threats}</div>
                <div class="stat-label">Total Threats</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{active_actors}</div>
                <div class="stat-label">Active Actors</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{high_severity}</div>
                <div class="stat-label">High Severity</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{countries}</div>
                <div class="stat-label">Countries</div>
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
    st.markdown('<div class="filter-group">', unsafe_allow_html=True)
    st.markdown("### 🔍 Filters")
    
    filter_mode = st.radio("Time Filter", ["All Data", "Year", "Month", "Quarter"], index=0)
    
    filtered_df = df.copy()
    
    if filter_mode == "Year":
        years = sorted(df['year'].unique(), reverse=True)
        selected_years = st.multiselect("Select Year(s)", options=years, default=years)
        filtered_df = filtered_df[filtered_df['year'].isin(selected_years)]
    
    elif filter_mode == "Month":
        selected_year = st.selectbox("Year", options=sorted(df['year'].unique(), reverse=True))
        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        selected_months = st.multiselect("Month(s)", options=months, default=months)
        filtered_df = filtered_df[(filtered_df['year'] == selected_year) & (filtered_df['month_name'].isin(selected_months))]
    
    elif filter_mode == "Quarter":
        selected_year = st.selectbox("Year", options=sorted(df['year'].unique(), reverse=True))
        quarters = sorted(df[df['year'] == selected_year]['quarter'].unique())
        selected_quarters = st.multiselect("Quarter(s)", options=quarters, default=quarters, format_func=lambda x: f"Q{x}")
        filtered_df = filtered_df[(filtered_df['year'] == selected_year) & (filtered_df['quarter'].isin(selected_quarters))]
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="filter-group">', unsafe_allow_html=True)
    st.markdown("### 🎯 Categories")
    
    selected_threat_types = st.multiselect("Threat Type", options=sorted(df['threat_type'].unique()), default=df['threat_type'].unique())
    selected_severity = st.multiselect("Severity", options=sorted(df['severity'].unique()), default=df['severity'].unique())
    selected_sectors = st.multiselect("Sector", options=sorted(df['sector'].unique()), default=df['sector'].unique())
    selected_countries = st.multiselect("Country", options=sorted(df['country'].unique()), default=df['country'].unique())
    
    filtered_df = filtered_df[
        (filtered_df['threat_type'].isin(selected_threat_types)) &
        (filtered_df['severity'].isin(selected_severity)) &
        (filtered_df['sector'].isin(selected_sectors)) &
        (filtered_df['country'].isin(selected_countries))
    ]
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="filter-group">', unsafe_allow_html=True)
    st.metric("Filtered Records", len(filtered_df))
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# CHARTS
# --------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    threat_counts = filtered_df['threat_type'].value_counts().reset_index()
    threat_counts.columns = ['Threat Type', 'Count']
    
    fig = px.pie(
        threat_counts,
        names='Threat Type',
        values='Count',
        hole=0.5,
        template=C["template"],
        color_discrete_sequence=px.colors.sequential.Reds
    )
    fig.update_layout(title="Threat Distribution", height=350)
    st.plotly_chart(fig, use_container_width=True, key="threat_pie")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    severity_counts = filtered_df['severity'].value_counts().reset_index()
    severity_counts.columns = ['Severity', 'Count']
    
    color_map = {'High': BRAND_RED, 'Medium': '#ffc107', 'Low': '#00ff88'}
    fig = px.bar(
        severity_counts,
        x='Severity',
        y='Count',
        template=C["template"],
        color='Severity',
        color_discrete_map=color_map,
        text='Count'
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(title="Severity Breakdown", height=350, showlegend=False)
    st.plotly_chart(fig, use_container_width=True, key="severity_bar")
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# TIMELINE
# --------------------------------------------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)

timeline_df = filtered_df.groupby(filtered_df['date'].dt.date).size().reset_index()
timeline_df.columns = ['Date', 'Count']

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=timeline_df['Date'],
    y=timeline_df['Count'],
    mode="lines",
    fill="tozeroy",
    line=dict(color='#00d4ff', width=2),
    fillcolor='rgba(0, 212, 255, 0.2)'
))
fig.update_layout(
    title="Daily Threat Activity",
    template=C["template"],
    height=300,
    xaxis_title="",
    yaxis_title="Number of Threats"
)
st.plotly_chart(fig, use_container_width=True, key="timeline")

st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# SECTOR & COUNTRY CHARTS
# --------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    sector_counts = filtered_df['sector'].value_counts().head(10).reset_index()
    sector_counts.columns = ['Sector', 'Count']
    
    fig = px.bar(
        sector_counts,
        y='Sector',
        x='Count',
        orientation='h',
        template=C["template"],
        color='Count',
        color_continuous_scale=[[0, '#141b3d'], [1, BRAND_RED]],
        text='Count'
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(title="Top Affected Sectors", height=350, showlegend=False)
    st.plotly_chart(fig, use_container_width=True, key="sector_bar")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    country_counts = filtered_df['country'].value_counts().head(10).reset_index()
    country_counts.columns = ['Country', 'Count']
    
    fig = px.bar(
        country_counts,
        y='Country',
        x='Count',
        orientation='h',
        template=C["template"],
        color='Count',
        color_continuous_scale=[[0, '#141b3d'], [1, BRAND_RED]],
        text='Count'
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(title="Geographic Distribution", height=350, showlegend=False)
    st.plotly_chart(fig, use_container_width=True, key="country_bar")
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# EXPORT & DATA MANAGEMENT
# --------------------------------------------------
with st.sidebar:
    st.markdown('<div class="filter-group">', unsafe_allow_html=True)
    st.markdown("### 📥 Export Report")
    
    report_format = st.radio("Format", ["CSV", "Summary CSV"], label_visibility="collapsed")
    
    if st.button("📄 Generate Report", use_container_width=True):
        if report_format == "CSV":
            # Full detailed report (no raw data shown on dashboard)
            csv_buffer = filtered_df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download Full Report (CSV)",
                data=csv_buffer,
                file_name=f"cyhawk_full_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            # Summary report
            import io
            summary_buffer = io.StringIO()
            summary_buffer.write("CyHawk Africa - Threat Intelligence Summary Report\n")
            summary_buffer.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            summary_buffer.write(f"Period: {filtered_df['date'].min()} to {filtered_df['date'].max()}\n\n")
            summary_buffer.write(f"Total Threats: {len(filtered_df)}\n")
            summary_buffer.write(f"High Severity: {len(filtered_df[filtered_df['severity'] == 'High'])}\n")
            summary_buffer.write(f"Unique Threat Actors: {filtered_df['actor'].nunique()}\n")
            summary_buffer.write(f"Countries Affected: {filtered_df['country'].nunique()}\n\n")
            summary_buffer.write("Top Threat Types:\n")
            summary_buffer.write(filtered_df['threat_type'].value_counts().to_string())
            summary_buffer.write("\n\nTop Affected Sectors:\n")
            summary_buffer.write(filtered_df['sector'].value_counts().to_string())
            
            st.download_button(
                label="⬇️ Download Summary Report (CSV)",
                data=summary_buffer.getvalue(),
                file_name=f"cyhawk_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Data update section
    st.markdown('<div class="filter-group">', unsafe_allow_html=True)
    st.markdown("### 📊 Update Data")
    st.info("Upload a new incidents.csv file to update the dashboard data.")
    
    uploaded_file = st.file_uploader("Upload CSV", type=['csv'], label_visibility="collapsed")
    
    if uploaded_file is not None:
        try:
            # Read the uploaded file
            new_df = pd.read_csv(uploaded_file)
            
            # Validate required columns
            required_columns = ['date', 'actor', 'country', 'threat_type', 'sector', 'severity', 'source']
            if all(col in new_df.columns for col in required_columns):
                # Save to data folder
                os.makedirs('data', exist_ok=True)
                new_df.to_csv('data/incidents.csv', index=False)
                st.success("✅ Data updated successfully!")
                st.info("🔄 Please refresh the page to see the updated data.")
                
                if st.button("🔄 Refresh Dashboard", use_container_width=True):
                    st.cache_data.clear()
                    st.rerun()
            else:
                st.error(f"❌ CSV must contain columns: {', '.join(required_columns)}")
        except Exception as e:
            st.error(f"❌ Error uploading file: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# FOOTER (NO RAW DATA DISPLAY)
# --------------------------------------------------
st.markdown(f"""
<div style="text-align:center;color:{C['muted']};padding:2rem;border-top:1px solid {C['border']};margin-top:2rem">
    <strong style="color:{BRAND_RED}">CyHawk Africa</strong> © {datetime.now().year} — Cyber Threat Intelligence Platform<br>
    <small>Dashboard showing aggregated intelligence metrics | Operational data restricted to authorized partners</small><br>
    <small style="opacity:0.7">Analyzing {len(filtered_df)} threat indicators from {len(df)} total records</small>
</div>
""", unsafe_allow_html=True)
