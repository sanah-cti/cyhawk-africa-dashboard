import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="CyHawk Africa - CTI Dashboard",
    page_icon="",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🛡️ CyHawk Africa - Cyber Threat Intelligence Dashboard")
st.markdown("---")

# Load data from CSV
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/incidents.csv')
        df['date'] = pd.to_datetime(df['date'])
        return df
    except FileNotFoundError:
        st.error("❌ Error: 'data/incidents.csv' file not found!")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.stop()

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Date range filter
if 'date' in df.columns:
    min_date = df['date'].min()
    max_date = df['date'].max()
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

selected_countries = st.sidebar.multiselect(
    "Select Countries",
    options=sorted(df['country'].unique()),
    default=df['country'].unique()
)

selected_severity = st.sidebar.multiselect(
    "Select Severity",
    options=sorted(df['severity'].unique()),
    default=df['severity'].unique()
)

selected_sectors = st.sidebar.multiselect(
    "Select Sectors",
    options=sorted(df['sector'].unique()),
    default=df['sector'].unique()
)

# Filter data
filtered_df = df[
    (df['country'].isin(selected_countries)) &
    (df['severity'].isin(selected_severity)) &
    (df['sector'].isin(selected_sectors))
]

# Apply date filter if available
if 'date' in df.columns and len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df['date'].dt.date >= date_range[0]) &
        (filtered_df['date'].dt.date <= date_range[1])
    ]

# Key Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Threats", len(filtered_df), delta=None)

with col2:
    high_severity = len(filtered_df[filtered_df['severity'] == 'High'])
    st.metric("High Severity", high_severity)

with col3:
    unique_actors = filtered_df['actor'].nunique()
    st.metric("Threat Actors", unique_actors)

with col4:
    affected_countries = filtered_df['country'].nunique()
    st.metric("Affected Countries", affected_countries)

st.markdown("---")

# Charts Row 1
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Threats by Severity")
    severity_counts = filtered_df['severity'].value_counts().reset_index()
    severity_counts.columns = ['Severity', 'Count']
    
    fig_severity = px.pie(
        severity_counts,
        values='Count',
        names='Severity',
        color='Severity',
        color_discrete_map={'High': '#ff4444', 'Medium': '#ffaa00', 'Low': '#44ff44'},
        hole=0.4
    )
    fig_severity.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=350
    )
    st.plotly_chart(fig_severity, use_container_width=True)

with col2:
    st.subheader("🎯 Threats by Sector")
    sector_counts = filtered_df['sector'].value_counts().reset_index()
    sector_counts.columns = ['Sector', 'Count']
    
    fig_sector = px.bar(
        sector_counts,
        x='Sector',
        y='Count',
        color='Count',
        color_continuous_scale='Reds'
    )
    fig_sector.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False,
        height=350
    )
    st.plotly_chart(fig_sector, use_container_width=True)

# Charts Row 2
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌍 Threats by Country")
    country_counts = filtered_df['country'].value_counts().reset_index()
    country_counts.columns = ['Country', 'Count']
    
    fig_country = px.bar(
        country_counts,
        x='Country',
        y='Count',
        color='Count',
        color_continuous_scale='Blues',
        text='Count'
    )
    fig_country.update_traces(textposition='outside')
    fig_country.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False,
        height=350
    )
    st.plotly_chart(fig_country, use_container_width=True)

with col2:
    st.subheader("⚠️ Threat Types Distribution")
    threat_counts = filtered_df['threat_type'].value_counts().reset_index()
    threat_counts.columns = ['Threat Type', 'Count']
    
    fig_threat = px.bar(
        threat_counts,
        y='Threat Type',
        x='Count',
        orientation='h',
        color='Count',
        color_continuous_scale='Oranges',
        text='Count'
    )
    fig_threat.update_traces(textposition='outside')
    fig_threat.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False,
        height=350
    )
    st.plotly_chart(fig_threat, use_container_width=True)

# Charts Row 3
col1, col2 = st.columns(2)

with col1:
    st.subheader("👤 Top Threat Actors")
    actor_counts = filtered_df['actor'].value_counts().head(10).reset_index()
    actor_counts.columns = ['Actor', 'Count']
    
    fig_actor = px.bar(
        actor_counts,
        x='Actor',
        y='Count',
        color='Count',
        color_continuous_scale='Purples',
        text='Count'
    )
    fig_actor.update_traces(textposition='outside')
    fig_actor.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False,
        height=350
    )
    fig_actor.update_xaxes(tickangle=45)
    st.plotly_chart(fig_actor, use_container_width=True)

with col2:
    st.subheader("📡 Intelligence Sources")
    source_counts = filtered_df['source'].value_counts().reset_index()
    source_counts.columns = ['Source', 'Count']
    
    fig_source = px.pie(
        source_counts,
        values='Count',
        names='Source',
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    fig_source.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=350
    )
    st.plotly_chart(fig_source, use_container_width=True)

# Timeline if date column exists
if 'date' in df.columns:
    st.markdown("---")
    st.subheader("📅 Threat Timeline")
    
    timeline_df = filtered_df.groupby(filtered_df['date'].dt.date).size().reset_index()
    timeline_df.columns = ['Date', 'Count']
    
    fig_timeline = px.line(
        timeline_df,
        x='Date',
        y='Count',
        markers=True
    )
    fig_timeline.update_traces(line_color='#00d4ff', marker=dict(size=8))
    fig_timeline.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=300,
        xaxis_title="Date",
        yaxis_title="Number of Threats"
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

st.markdown("---")

# Data Table
st.subheader("📋 Detailed Threat Intelligence Data")

# Column configuration
column_config = {
    "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
    "severity": st.column_config.TextColumn("Severity"),
    "actor": st.column_config.TextColumn("Threat Actor"),
    "country": st.column_config.TextColumn("Country"),
    "threat_type": st.column_config.TextColumn("Threat Type"),
    "sector": st.column_config.TextColumn("Sector"),
    "source": st.column_config.TextColumn("Source")
}

st.dataframe(
    filtered_df,
    use_container_width=True,
    height=400,
    column_config=column_config
)

# Statistics summary
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Summary Statistics")
st.sidebar.metric("Total Records", len(df))
st.sidebar.metric("Filtered Records", len(filtered_df))

# Export functionality
st.sidebar.markdown("---")
st.sidebar.subheader("📥 Export Data")
csv = filtered_df.to_csv(index=False)
st.sidebar.download_button(
    label="Download Filtered Data (CSV)",
    data=csv,
    file_name=f"cti_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv"
)
