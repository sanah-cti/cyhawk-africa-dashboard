import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

# Page configuration
st.set_page_config(
    page_title="CyHawk Africa - Cyber Threat Intelligence Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme in session state
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# Theme toggle function
def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# Theme configurations
def get_theme_colors():
    if st.session_state.theme == 'dark':
        return {
            'bg_primary': '#0e1117',
            'bg_secondary': '#1e2130',
            'bg_card': '#262730',
            'text_primary': '#ffffff',
            'text_secondary': '#b0b0b0',
            'accent': '#00d4ff',
            'border': '#2d2d2d',
            'chart_bg': 'rgba(0,0,0,0)',
            'plotly_template': 'plotly_dark'
        }
    else:
        return {
            'bg_primary': '#ffffff',
            'bg_secondary': '#f8f9fa',
            'bg_card': '#ffffff',
            'text_primary': '#1f1f1f',
            'text_secondary': '#666666',
            'accent': '#0066cc',
            'border': '#e0e0e0',
            'chart_bg': 'rgba(255,255,255,0)',
            'plotly_template': 'plotly_white'
        }

colors = get_theme_colors()

# Custom CSS with theme support
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {{
        font-family: 'Inter', sans-serif;
    }}
    
    .main {{
        background-color: {colors['bg_primary']};
    }}
    
    .stApp {{
        background: {colors['bg_primary']};
    }}
    
    /* Header styling */
    .dashboard-header {{
        background: linear-gradient(135deg, {colors['accent']} 0%, #6366f1 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }}
    
    .dashboard-title {{
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-align: center;
    }}
    
    .dashboard-subtitle {{
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        font-weight: 400;
        text-align: center;
        margin-top: 0.5rem;
    }}
    
    /* Metric cards */
    .metric-card {{
        background: {colors['bg_card']};
        border: 1px solid {colors['border']};
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s, box-shadow 0.2s;
        height: 100%;
    }}
    
    .metric-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }}
    
    .metric-value {{
        font-size: 2.5rem;
        font-weight: 700;
        color: {colors['accent']};
        margin: 0.5rem 0;
    }}
    
    .metric-label {{
        font-size: 0.9rem;
        color: {colors['text_secondary']};
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }}
    
    .metric-icon {{
        font-size: 2rem;
        opacity: 0.8;
    }}
    
    /* Section headers */
    .section-header {{
        color: {colors['text_primary']};
        font-size: 1.5rem;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid {colors['accent']};
    }}
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background-color: {colors['bg_secondary']};
        border-right: 1px solid {colors['border']};
    }}
    
    [data-testid="stSidebar"] .stMarkdown {{
        color: {colors['text_primary']};
    }}
    
    /* Cards for charts */
    .chart-container {{
        background: {colors['bg_card']};
        border: 1px solid {colors['border']};
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }}
    
    /* Button styling */
    .stButton > button {{
        background: linear-gradient(135deg, {colors['accent']} 0%, #6366f1 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }}
    
    /* Theme toggle button */
    .theme-toggle {{
        position: fixed;
        top: 4rem;
        right: 2rem;
        z-index: 999;
        background: {colors['bg_card']};
        border: 1px solid {colors['border']};
        border-radius: 50%;
        width: 50px;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s;
    }}
    
    .theme-toggle:hover {{
        transform: scale(1.1);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }}
    
    /* Dataframe styling */
    .dataframe {{
        border: 1px solid {colors['border']} !important;
        border-radius: 8px;
    }}
    
    /* Filter section */
    .filter-container {{
        background: {colors['bg_card']};
        border: 1px solid {colors['border']};
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }}
    
    /* Stats badge */
    .stats-badge {{
        display: inline-block;
        background: {colors['accent']};
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }}
    
    /* Severity badges */
    .severity-high {{
        background: #ff4444;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }}
    
    .severity-medium {{
        background: #ffaa00;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }}
    
    .severity-low {{
        background: #44ff44;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }}
    
    </style>
""", unsafe_allow_html=True)

# Theme toggle button in header
col1, col2, col3 = st.columns([1, 6, 1])
with col3:
    theme_icon = "🌙" if st.session_state.theme == 'dark' else "☀️"
    if st.button(theme_icon, key="theme_toggle", help="Toggle theme"):
        toggle_theme()
        st.rerun()

# Dashboard Header
st.markdown(f"""
    <div class="dashboard-header">
        <h1 class="dashboard-title">🛡️ CyHawk Africa</h1>
        <p class="dashboard-subtitle">Cyber Threat Intelligence Dashboard</p>
    </div>
""", unsafe_allow_html=True)

# Load data from CSV
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/incidents.csv')
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['month_name'] = df['date'].dt.strftime('%B')
        df['quarter'] = df['date'].dt.quarter
        df['day_of_week'] = df['date'].dt.day_name()
        return df
    except FileNotFoundError:
        st.error("❌ Error: 'data/incidents.csv' file not found!")
        st.info("Please ensure your data file is located at: data/incidents.csv")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.stop()

df = load_data()

# Sidebar filters
with st.sidebar:
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    st.markdown("## 🔍 Filters")
    
    # Filter Type Selection
    filter_mode = st.radio(
        "Time Filter Mode",
        ["Date Range", "Year", "Month", "Quarter", "Daily"],
        index=0,
        help="Select how you want to filter by time"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    filtered_df = df.copy()
    
    # Apply date filters based on mode
    if filter_mode == "Date Range":
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        min_date = df['date'].min().date()
        max_date = df['date'].max().date()
        date_range = st.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        if len(date_range) == 2:
            filtered_df = filtered_df[
                (filtered_df['date'].dt.date >= date_range[0]) &
                (filtered_df['date'].dt.date <= date_range[1])
            ]
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif filter_mode == "Year":
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        years = sorted(df['year'].unique(), reverse=True)
        selected_years = st.multiselect(
            "Select Year(s)",
            options=years,
            default=years
        )
        filtered_df = filtered_df[filtered_df['year'].isin(selected_years)]
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif filter_mode == "Month":
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        selected_year = st.selectbox(
            "Select Year",
            options=sorted(df['year'].unique(), reverse=True)
        )
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November', 'December']
        selected_months = st.multiselect(
            "Select Month(s)",
            options=months,
            default=months
        )
        filtered_df = filtered_df[
            (filtered_df['year'] == selected_year) &
            (filtered_df['month_name'].isin(selected_months))
        ]
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif filter_mode == "Quarter":
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        selected_year = st.selectbox(
            "Select Year",
            options=sorted(df['year'].unique(), reverse=True)
        )
        quarters = sorted(df['quarter'].unique())
        selected_quarters = st.multiselect(
            "Select Quarter(s)",
            options=quarters,
            default=quarters,
            format_func=lambda x: f"Q{x}"
        )
        filtered_df = filtered_df[
            (filtered_df['year'] == selected_year) &
            (filtered_df['quarter'].isin(selected_quarters))
        ]
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif filter_mode == "Daily":
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        selected_date = st.date_input(
            "Select Date",
            value=df['date'].max().date(),
            min_value=df['date'].min().date(),
            max_value=df['date'].max().date()
        )
        filtered_df = filtered_df[filtered_df['date'].dt.date == selected_date]
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Additional filters
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    st.markdown("### Additional Filters")
    
    selected_threat_types = st.multiselect(
        "Threat Type",
        options=sorted(df['threat_type'].unique()),
        default=df['threat_type'].unique()
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
    
    selected_severity = st.multiselect(
        "Severity",
        options=sorted(df['severity'].unique()),
        default=df['severity'].unique()
    )
    
    selected_countries = st.multiselect(
        "Country",
        options=sorted(df['country'].unique()),
        default=df['country'].unique()
    )
    
    selected_sources = st.multiselect(
        "Source",
        options=sorted(df['source'].unique()),
        default=df['source'].unique()
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply additional filters
    filtered_df = filtered_df[
        (filtered_df['threat_type'].isin(selected_threat_types)) &
        (filtered_df['sector'].isin(selected_sectors)) &
        (filtered_df['actor'].isin(selected_actors)) &
        (filtered_df['severity'].isin(selected_severity)) &
        (filtered_df['country'].isin(selected_countries)) &
        (filtered_df['source'].isin(selected_sources))
    ]
    
    # Summary Statistics
    st.markdown("---")
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    st.markdown("###  Statistics")
    st.metric("Total Records", len(df))
    st.metric("Filtered Records", len(filtered_df))
    if len(filtered_df) > 0:
        filter_percentage = (len(filtered_df) / len(df)) * 100
        st.metric("Coverage", f"{filter_percentage:.1f}%")
    st.markdown('</div>', unsafe_allow_html=True)

# Key Metrics
st.markdown('<p class="section-header">📊 Key Metrics Overview</p>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

metrics = [
    ("Total Threats", len(filtered_df), "🎯"),
    ("High Severity", len(filtered_df[filtered_df['severity'] == 'High']), "🔴"),
    ("Threat Actors", filtered_df['actor'].nunique(), "👤"),
    ("Countries", filtered_df['country'].nunique(), "🌍"),
    ("Sectors", filtered_df['sector'].nunique(), "🏢")
]

for col, (label, value, icon) in zip([col1, col2, col3, col4, col5], metrics):
    with col:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">{icon}</div>
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Charts Row 1
st.markdown('<p class="section-header">📈 Threat Analysis</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("#### 📊 Threats by Severity")
    severity_counts = filtered_df['severity'].value_counts().reset_index()
    severity_counts.columns = ['Severity', 'Count']
    
    fig_severity = px.pie(
        severity_counts,
        values='Count',
        names='Severity',
        color='Severity',
        color_discrete_map={'High': '#ff4444', 'Medium': '#ffaa00', 'Low': '#44ff44'},
        hole=0.4,
        template=colors['plotly_template']
    )
    fig_severity.update_layout(
        paper_bgcolor=colors['chart_bg'],
        plot_bgcolor=colors['chart_bg'],
        font=dict(color=colors['text_primary']),
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_severity, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("#### ⚠️ Threat Types Distribution")
    threat_counts = filtered_df['threat_type'].value_counts().reset_index()
    threat_counts.columns = ['Threat Type', 'Count']
    
    fig_threat = px.bar(
        threat_counts,
        x='Threat Type',
        y='Count',
        color='Count',
        color_continuous_scale='Reds',
        text='Count',
        template=colors['plotly_template']
    )
    fig_threat.update_traces(textposition='outside')
    fig_threat.update_layout(
        paper_bgcolor=colors['chart_bg'],
        plot_bgcolor=colors['chart_bg'],
        font=dict(color=colors['text_primary']),
        showlegend=False,
        height=400,
        xaxis_title="",
        yaxis_title="Number of Threats"
    )
    st.plotly_chart(fig_threat, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Charts Row 2
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("#### 🎯 Threats by Sector")
    sector_counts = filtered_df['sector'].value_counts().reset_index()
    sector_counts.columns = ['Sector', 'Count']
    
    fig_sector = px.bar(
        sector_counts,
        y='Sector',
        x='Count',
        orientation='h',
        color='Count',
        color_continuous_scale='Blues',
        text='Count',
        template=colors['plotly_template']
    )
    fig_sector.update_traces(textposition='outside')
    fig_sector.update_layout(
        paper_bgcolor=colors['chart_bg'],
        plot_bgcolor=colors['chart_bg'],
        font=dict(color=colors['text_primary']),
        showlegend=False,
        height=400,
        xaxis_title="Number of Threats",
        yaxis_title=""
    )
    st.plotly_chart(fig_sector, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("#### 🌍 Threats by Country")
    country_counts = filtered_df['country'].value_counts().reset_index()
    country_counts.columns = ['Country', 'Count']
    
    fig_country = px.bar(
        country_counts,
        x='Country',
        y='Count',
        color='Count',
        color_continuous_scale='Greens',
        text='Count',
        template=colors['plotly_template']
    )
    fig_country.update_traces(textposition='outside')
    fig_country.update_layout(
        paper_bgcolor=colors['chart_bg'],
        plot_bgcolor=colors['chart_bg'],
        font=dict(color=colors['text_primary']),
        showlegend=False,
        height=400,
        xaxis_title="",
        yaxis_title="Number of Threats"
    )
    st.plotly_chart(fig_country, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Charts Row 3
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("#### 👤 Top 10 Threat Actors")
    actor_counts = filtered_df['actor'].value_counts().head(10).reset_index()
    actor_counts.columns = ['Actor', 'Count']
    
    fig_actor = px.bar(
        actor_counts,
        y='Actor',
        x='Count',
        orientation='h',
        color='Count',
        color_continuous_scale='Purples',
        text='Count',
        template=colors['plotly_template']
    )
    fig_actor.update_traces(textposition='outside')
    fig_actor.update_layout(
        paper_bgcolor=colors['chart_bg'],
        plot_bgcolor=colors['chart_bg'],
        font=dict(color=colors['text_primary']),
        showlegend=False,
        height=400,
        xaxis_title="Number of Threats",
        yaxis_title=""
    )
    st.plotly_chart(fig_actor, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("#### 📡 Intelligence Sources")
    source_counts = filtered_df['source'].value_counts().reset_index()
    source_counts.columns = ['Source', 'Count']
    
    fig_source = px.pie(
        source_counts,
        values='Count',
        names='Source',
        color_discrete_sequence=px.colors.sequential.Viridis,
        template=colors['plotly_template']
    )
    fig_source.update_layout(
        paper_bgcolor=colors['chart_bg'],
        plot_bgcolor=colors['chart_bg'],
        font=dict(color=colors['text_primary']),
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_source, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Timeline Chart
st.markdown("---")
st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.markdown('<p class="section-header">📅 Threat Timeline</p>', unsafe_allow_html=True)

timeline_df = filtered_df.groupby(filtered_df['date'].dt.date).size().reset_index()
timeline_df.columns = ['Date', 'Count']

fig_timeline = go.Figure()
fig_timeline.add_trace(go.Scatter(
    x=timeline_df['Date'],
    y=timeline_df['Count'],
    mode='lines+markers',
    line=dict(color=colors['accent'], width=3),
    marker=dict(size=8, color=colors['accent']),
    fill='tozeroy',
    fillcolor=f"rgba({int(colors['accent'][1:3], 16)}, {int(colors['accent'][3:5], 16)}, {int(colors['accent'][5:7], 16)}, 0.2)"
))

fig_timeline.update_layout(
    paper_bgcolor=colors['chart_bg'],
    plot_bgcolor=colors['chart_bg'],
    font=dict(color=colors['text_primary']),
    height=350,
    xaxis_title="Date",
    yaxis_title="Number of Threats",
    hovermode='x unified',
    template=colors['plotly_template']
)
st.plotly_chart(fig_timeline, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# Data Table
st.markdown('<p class="section-header">📋 Detailed Threat Intelligence Data</p>', unsafe_allow_html=True)
st.markdown('<div class="chart-container">', unsafe_allow_html=True)

display_columns = ['date', 'actor', 'country', 'threat_type', 'sector', 'severity', 'source']

# Add search functionality
search_term = st.text_input("🔍 Search in data", "", placeholder="Type to search...")
if search_term:
    mask = filtered_df[display_columns].astype(str).apply(
        lambda x: x.str.contains(search_term, case=False, na=False)
    ).any(axis=1)
    display_df = filtered_df[mask]
else:
    display_df = filtered_df

st.dataframe(
    display_df[display_columns],
    use_container_width=True,
    height=400
)
st.markdown('</div>', unsafe_allow_html=True)

# Report Generation Functions
def generate_csv_report():
    """Generate CSV report"""
    csv_buffer = io.StringIO()
    
    csv_buffer.write("CyHawk Africa - Cyber Threat Intelligence Report\n")
    csv_buffer.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    csv_buffer.write(f"Filter Mode: {filter_mode}\n")
    csv_buffer.write(f"Total Threats: {len(filtered_df)}\n")
    csv_buffer.write(f"High Severity Threats: {len(filtered_df[filtered_df['severity'] == 'High'])}\n")
    csv_buffer.write(f"Unique Threat Actors: {filtered_df['actor'].nunique()}\n")
    csv_buffer.write(f"Affected Countries: {filtered_df['country'].nunique()}\n")
    csv_buffer.write(f"Affected Sectors: {filtered_df['sector'].nunique()}\n\n")
    
    csv_buffer.write("Threats by Severity\n")
    severity_counts = filtered_df['severity'].value_counts()
    severity_counts.to_csv(csv_buffer)
    csv_buffer.write("\n")
    
    csv_buffer.write("Threats by Sector\n")
    sector_counts = filtered_df['sector'].value_counts()
    sector_counts.to_csv(csv_buffer)
    csv_buffer.write("\n")
    
    csv_buffer.write("Threats by Country\n")
    country_counts = filtered_df['country'].value_counts()
    country_counts.to_csv(csv_buffer)
    csv_buffer.write("\n")
    
    csv_buffer.write("Top 10 Threat Actors\n")
    actor_counts = filtered_df['actor'].value_counts().head(10)
    actor_counts.to_csv(csv_buffer)
    csv_buffer.write("\n")
    
    csv_buffer.write("Detailed Threat Intelligence Data\n")
    filtered_df[display_columns].to_csv(csv_buffer, index=False)
    
    return csv_buffer.getvalue()

def generate_pdf_report():
    """Generate PDF report"""
    pdf_buffer = io.BytesIO()
    
    with PdfPages(pdf_buffer) as pdf:
        # Page 1: Summary
        fig, ax = plt.subplots(figsize=(11, 8.5))
        fig.patch.set_facecolor('white')
        ax.axis('off')
        
        summary_text = f"""
        CyHawk Africa - Cyber Threat Intelligence Report
        
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        Filter Mode: {filter_mode}
        
        KEY METRICS
        ────────────────────────────────────────────────
        Total Threats: {len(filtered_df)}
        High Severity: {len(filtered_df[filtered_df['severity'] == 'High'])}
        Medium Severity: {len(filtered_df[filtered_df['severity'] == 'Medium'])}
        Low Severity: {len(filtered_df[filtered_df['severity'] == 'Low'])}
        
        Unique Threat Actors: {filtered_df['actor'].nunique()}
        Affected Countries: {filtered_df['country'].nunique()}
        Affected Sectors: {filtered_df['sector'].nunique()}
        
        THREAT DISTRIBUTION
        ────────────────────────────────────────────────
        """
        
        threat_types = filtered_df['threat_type'].value_counts()
        for threat_type, count in threat_types.items():
            summary_text += f"\n{threat_type}: {count}"
        
        ax.text(0.1, 0.9, summary_text, transform=ax.transAxes,
                fontsize=12, verticalalignment='top', fontfamily='monospace')
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Page 2: Severity Distribution
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 8.5))
        fig.suptitle('Threat Analysis', fontsize=16, fontweight='bold')
        
        severity_counts = filtered_df['severity'].value_counts()
        colors_sev = {'High': '#ff4444', 'Medium': '#ffaa00', 'Low': '#44ff44'}
        plot_colors = [colors_sev.get(x, '#888888') for x in severity_counts.index]
        ax1.pie(severity_counts.values, labels=severity_counts.index, autopct='%1.1f%%',
                colors=plot_colors, startangle=90)
        ax1.set_title('Threats by Severity')
        
        sector_counts = filtered_df['sector'].value_counts().head(10)
        ax2.barh(range(len(sector_counts)), sector_counts.values, color='steelblue')
        ax2.set_yticks(range(len(sector_counts)))
        ax2.set_yticklabels(sector_counts.index)
        ax2.set_xlabel('Number of Threats')
        ax2.set_title('Top 10 Affected Sectors')
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
    
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()

# Report Generation Section in Sidebar
with st.sidebar:
    st.markdown("---")
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    st.markdown("### 📥 Generate Report")
    
    report_format = st.radio(
        "Select Format",
        ["CSV", "PDF"],
        help="Choose the format for your report"
    )
    
    if st.button("📄 Generate Report", use_container_width=True):
        with st.spinner("Generating report..."):
            if report_format == "CSV":
                csv_data = generate_csv_report()
                st.download_button(
                    label="⬇️ Download CSV Report",
                    data=csv_data,
                    file_name=f"cti_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                st.success("✅ CSV report generated!")
            
            elif report_format == "PDF":
                pdf_data = generate_pdf_report()
                st.download_button(
                    label="⬇️ Download PDF Report",
                    data=pdf_data,
                    file_name=f"cti_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                st.success("✅ PDF report generated!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick export
    st.markdown("---")
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    st.markdown("###  Quick Export")
    csv_raw = filtered_df.to_csv(index=False)
    st.download_button(
        label="⬇️ Export Raw Data",
        data=csv_raw,
        file_name=f"cti_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(f"""
    <div style='text-align: center; color: {colors['text_secondary']}; padding: 2rem;'>
        <p> <strong>CyHawk Africa</strong> | Cyber Threat Intelligence Platform</p>
        <p style='font-size: 0.9rem;'>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
""", unsafe_allow_html=True)
