import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Import navigation utilities
try:
    from navigation_utils import add_logo_and_branding, set_page_config as custom_set_page_config
    custom_set_page_config(
        page_title="Threat Actors | CyHawk Africa",
        page_icon="🎯",
        layout="wide"
    )
    add_logo_and_branding()
except ImportError:
    st.set_page_config(
        page_title="Threat Actors | CyHawk Africa",
        page_icon="🎯",
        layout="wide"
    )

# Theme
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

CYHAWK_RED = "#C41E3A"
CYHAWK_RED_DARK = "#9A1529"

# Initialize view all state
if 'show_all_actors' not in st.session_state:
    st.session_state.show_all_actors = False

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
            "danger": "#DA3633",
            "warning": "#ffc107",
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
        "danger": "#D1242F",
        "warning": "#f59e0b",
        "template": "plotly_white"
    }

C = theme_config()

# Simplified CSS for containers
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* {{ font-family: 'Inter', sans-serif; }}
.main {{ background-color: {C['bg']}; }}
.stApp {{ background: {C['bg']}; }}

.page-header {{
    background: linear-gradient(135deg, {C['accent']} 0%, {CYHAWK_RED_DARK} 100%);
    padding: 3rem 2rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    text-align: center;
}}

.page-title {{
    color: white;
    font-size: 2.5rem;
    font-weight: 700;
    margin: 0;
}}

.page-subtitle {{
    color: rgba(255,255,255,0.9);
    font-size: 1.1rem;
    margin-top: 0.5rem;
}}

/* Container styling for square cards */
.stContainer {{
    position: relative;
}}

[data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] {{
    gap: 1rem;
}}
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    try:
        csv_path = 'data/incidents.csv'
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date'])
            
            categorical_columns = ['actor', 'country', 'threat_type', 'sector', 'severity', 'source']
            for col in categorical_columns:
                if col in df.columns:
                    df[col] = df[col].fillna('Unknown').astype(str)
            
            return df
        else:
            return pd.DataFrame()
    except:
        return pd.DataFrame()

df = load_data()

# Function to determine threat level
def determine_threat_level(actor_name, total_attacks, high_severity, countries, sectors, actor_type):
    """Determine threat level based on multiple factors"""
    # Ransomware groups
    ransomware_keywords = ['ransomware', 'revil', 'lockbit', 'darkside', 'conti', 'maze', 'ryuk']
    if any(keyword in actor_name.lower() for keyword in ransomware_keywords):
        return 'Critical'
    
    if any(keyword in actor_type.lower() for keyword in ransomware_keywords):
        return 'Critical'
    
    # High attack volume
    if total_attacks > 50:
        return 'Critical'
    
    # High severity attacks
    if high_severity > 10:
        return 'Critical'
    
    # Wide geographic spread
    if countries > 3:
        return 'Critical'
    
    # Multiple sectors
    if sectors > 5:
        return 'Critical'
    
    # APT groups
    apt_keywords = ['apt', 'fancy bear', 'lazarus', 'equation', 'turla']
    if any(keyword in actor_name.lower() for keyword in apt_keywords):
        return 'Critical'
    
    return 'High'

# Header
st.markdown(f"""
<div class="page-header">
    <h1 class="page-title">Threat Actor Intelligence</h1>
    <p class="page-subtitle">Comprehensive profiles of active threat actors targeting African organizations</p>
</div>
""", unsafe_allow_html=True)

# Get actor statistics
if len(df) > 0:
    actor_stats = df.groupby('actor').agg({
        'date': 'count',
        'severity': lambda x: (x == 'High').sum(),
        'country': 'nunique',
        'sector': 'nunique'
    }).reset_index()
    actor_stats.columns = ['actor', 'total_attacks', 'high_severity', 'countries', 'sectors']
    actor_stats = actor_stats.sort_values('total_attacks', ascending=False)
    
    # Threat actor profiles
    actor_profiles = {
        'APT28': {'alias': 'Fancy Bear, Sofacy', 'origin': 'Russia', 'active_since': '2007', 'type': 'State-Sponsored (GRU)'},
        'Lazarus Group': {'alias': 'HIDDEN COBRA', 'origin': 'North Korea', 'active_since': '2009', 'type': 'State-Sponsored (RGB)'},
        'Anonymous Sudan': {'alias': 'AnonymousSudan', 'origin': 'Sudan (Disputed)', 'active_since': '2023', 'type': 'Hacktivist'},
        'DarkSide': {'alias': 'DarkSide Ransomware', 'origin': 'Eastern Europe', 'active_since': '2020', 'type': 'Cybercrime (Ransomware)'},
        'REvil': {'alias': 'Sodinokibi', 'origin': 'Russia', 'active_since': '2019', 'type': 'Cybercrime (Ransomware)'},
    }
    
    # Add default profiles for unknown actors
    for actor_name in actor_stats['actor'].unique():
        if actor_name not in actor_profiles:
            actor_profiles[actor_name] = {
                'alias': 'Unknown',
                'origin': 'Unknown',
                'active_since': 'Unknown',
                'type': 'Unclassified',
            }
    
    # Calculate threat levels
    actor_stats['threat_level'] = actor_stats.apply(
        lambda row: determine_threat_level(
            row['actor'], row['total_attacks'], row['high_severity'],
            row['countries'], row['sectors'],
            actor_profiles.get(row['actor'], {}).get('type', 'Unknown')
        ), axis=1
    )
    
    # Filters
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        search_term = st.text_input("Search Threat Actors", placeholder="Search by name, origin, or type...")
    
    with col2:
        threat_filter = st.selectbox("Threat Level", ["All", "Critical", "High"])
    
    with col3:
        sort_by = st.selectbox("Sort By", ["Total Attacks", "High Severity", "Alphabetical"])
    
    with col4:
        st.markdown("<div style='margin-bottom: 8px;'>&nbsp;</div>", unsafe_allow_html=True)
        view_all_btn = st.button(
            "View All Actors" if not st.session_state.show_all_actors else "Show Top 12",
            use_container_width=True,
            type="primary"
        )
        if view_all_btn:
            st.session_state.show_all_actors = not st.session_state.show_all_actors
            st.rerun()
    
    # Apply filters
    filtered_stats = actor_stats.copy()
    
    if search_term:
        filtered_stats = filtered_stats[
            filtered_stats['actor'].str.contains(search_term, case=False, na=False)
        ]
    
    if threat_filter != "All":
        filtered_stats = filtered_stats[filtered_stats['threat_level'] == threat_filter]
    
    # Sort
    if sort_by == "Total Attacks":
        filtered_stats = filtered_stats.sort_values('total_attacks', ascending=False)
    elif sort_by == "High Severity":
        filtered_stats = filtered_stats.sort_values('high_severity', ascending=False)
    else:
        filtered_stats = filtered_stats.sort_values('actor')
    
    # Determine how many to show
    num_to_show = len(filtered_stats) if st.session_state.show_all_actors else min(12, len(filtered_stats))
    actors_to_display = filtered_stats.head(num_to_show)
    
    # Display in 4-column grid
    num_cols = 4
    num_actors = len(actors_to_display)
    
    for i in range(0, num_actors, num_cols):
        cols = st.columns(num_cols, gap="medium")
        
        for j in range(num_cols):
            if i + j < num_actors:
                row = actors_to_display.iloc[i + j]
                actor_name = row['actor']
                profile = actor_profiles.get(actor_name, {})
                threat_level = row['threat_level']
                
                with cols[j]:
                    # Container for square card
                    with st.container(border=True):
                        # Threat level badge
                        badge_color = C['danger'] if threat_level == 'Critical' else '#ff6b6b'
                        st.markdown(f"""
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                                <h3 style="margin: 0; font-size: 1.1rem; font-weight: 700; color: {C['text']}; flex: 1; padding-right: 1rem;">
                                    {actor_name}
                                </h3>
                                <span style="background: {badge_color}; color: white; padding: 0.25rem 0.6rem; 
                                      border-radius: 12px; font-size: 0.65rem; font-weight: 700; 
                                      text-transform: uppercase; white-space: nowrap;">
                                    {threat_level}
                                </span>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Alias
                        st.markdown(f"""
                            <p style="font-size: 0.8rem; color: {C['text_secondary']}; 
                                 font-style: italic; margin: 0 0 1rem 0;">
                                {profile.get('alias', 'Unknown')}
                            </p>
                        """, unsafe_allow_html=True)
                        
                        # Info
                        st.markdown(f"""
                            <div style="font-size: 0.85rem; color: {C['text_secondary']}; 
                                 margin-bottom: 1rem; line-height: 1.6;">
                                <div><strong style="color: {C['text_muted']};">Origin:</strong> {profile.get('origin', 'Unknown')}</div>
                                <div><strong style="color: {C['text_muted']};">Type:</strong> {profile.get('type', 'Unknown')}</div>
                                <div><strong style="color: {C['text_muted']};">Active:</strong> Since {profile.get('active_since', 'Unknown')}</div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Stats
                        stat_col1, stat_col2, stat_col3 = st.columns(3)
                        with stat_col1:
                            st.metric("Attacks", int(row['total_attacks']), label_visibility="visible")
                        with stat_col2:
                            st.metric("Countries", int(row['countries']), label_visibility="visible")
                        with stat_col3:
                            st.metric("Sectors", int(row['sectors']), label_visibility="visible")
                        
                        # View Profile button
                        if st.button("View Profile", key=f"view_{actor_name}", use_container_width=True):
                            st.session_state.selected_actor = actor_name
                            st.query_params["actor"] = actor_name
                            # Try different possible page names
                            try:
                                st.switch_page("pages/2_📋_Actor_Profile.py")
                            except:
                                try:
                                    st.switch_page("pages/Actor_Profile.py")
                                except:
                                    st.error("Actor Profile page not found. Please check the page filename.")
    
    # Show status
    st.markdown("---")
    if st.session_state.show_all_actors:
        st.success(f"✅ Showing all {num_actors} threat actors")
    else:
        st.info(f"ℹ️ Showing top {num_to_show} of {len(filtered_stats)} threat actors")
    
else:
    st.warning("⚠️ No threat actor data available. Please load incidents data.")

# Summary statistics
if len(df) > 0:
    st.markdown("---")
    st.subheader("Threat Actor Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Threat Actors", len(actor_stats))
    
    with col2:
        critical_count = len(actor_stats[actor_stats['threat_level'] == 'Critical'])
        st.metric("Critical Threat Actors", critical_count)
    
    with col3:
        st.metric("Total Attacks Tracked", int(actor_stats['total_attacks'].sum()))
    
    with col4:
        st.metric("High Severity Attacks", int(actor_stats['high_severity'].sum()))
