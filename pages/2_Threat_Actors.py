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

# CSS
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

/* Square card styling */
.actor-card-container {{
    background: {C['card']};
    border: 2px solid {C['border']};
    border-radius: 12px;
    padding: 1.5rem;
    transition: all 0.3s ease;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    aspect-ratio: 1;
    display: flex;
    flex-direction: column;
}}

.actor-card-container:hover {{
    transform: translateY(-6px);
    box-shadow: 0 12px 32px rgba(196, 30, 58, 0.3);
    border-color: {C['accent']};
}}

.actor-card-container::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, {C['accent']} 0%, {CYHAWK_RED_DARK} 100%);
}}

.threat-badge {{
    position: absolute;
    top: 1rem;
    right: 1rem;
    padding: 0.3rem 0.8rem;
    border-radius: 12px;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

.threat-critical {{ 
    background: {C['danger']}; 
    color: white;
    box-shadow: 0 2px 8px rgba(218, 54, 51, 0.3);
}}

.threat-high {{ 
    background: #ff6b6b; 
    color: white;
    box-shadow: 0 2px 8px rgba(255, 107, 107, 0.3);
}}

.actor-name-text {{
    font-size: 1.2rem;
    font-weight: 700;
    color: {C['text']};
    margin: 0 0 0.5rem 0;
    padding-right: 5rem;
    line-height: 1.3;
}}

.actor-alias {{
    font-size: 0.8rem;
    color: {C['text_secondary']};
    font-style: italic;
    margin-bottom: 1rem;
}}

.actor-info {{
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    margin-bottom: 1rem;
    flex-grow: 1;
}}

.info-row {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.85rem;
    color: {C['text_secondary']};
}}

.info-label {{
    font-weight: 600;
    min-width: 70px;
    color: {C['text_muted']};
}}

.actor-stats-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
    margin-top: auto;
    padding-top: 1rem;
    border-top: 1px solid {C['border']};
}}

.stat-box {{
    text-align: center;
}}

.stat-value {{
    font-size: 1.4rem;
    font-weight: 700;
    color: {C['accent']};
    line-height: 1;
}}

.stat-label {{
    font-size: 0.65rem;
    color: {C['text_muted']};
    text-transform: uppercase;
    margin-top: 0.25rem;
    letter-spacing: 0.5px;
}}

@media (max-width: 768px) {{
    .page-title {{
        font-size: 2rem;
    }}
    .actor-name-text {{
        font-size: 1.1rem;
    }}
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

# Function to determine threat level based on actor activity
def determine_threat_level(actor_name, total_attacks, high_severity, countries, sectors, actor_type):
    """
    Determine threat level based on multiple factors:
    - Ransomware groups: Critical
    - Top attackers (>50 attacks): Critical
    - High severity attacks (>10): Critical
    - Wide geographic spread (>3 countries): Critical
    - Multiple sectors (>5): Critical
    - Otherwise: High
    """
    # Check if ransomware group
    ransomware_keywords = ['ransomware', 'revil', 'lockbit', 'darkside', 'conti', 'maze', 'ryuk']
    if any(keyword in actor_name.lower() for keyword in ransomware_keywords):
        return 'Critical'
    
    if any(keyword in actor_type.lower() for keyword in ransomware_keywords):
        return 'Critical'
    
    # Check attack volume
    if total_attacks > 50:
        return 'Critical'
    
    # Check high severity attacks
    if high_severity > 10:
        return 'Critical'
    
    # Check geographic spread
    if countries > 3:
        return 'Critical'
    
    # Check sector diversity
    if sectors > 5:
        return 'Critical'
    
    # Check for state-sponsored APT groups
    apt_keywords = ['apt', 'fancy bear', 'lazarus', 'equation group', 'turla']
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
    
    # Threat actor profiles database
    actor_profiles = {
        'APT28': {
            'alias': 'Fancy Bear, Sofacy',
            'origin': 'Russia',
            'active_since': '2007',
            'type': 'State-Sponsored (GRU)',
        },
        'Lazarus Group': {
            'alias': 'HIDDEN COBRA, Guardians of Peace',
            'origin': 'North Korea',
            'active_since': '2009',
            'type': 'State-Sponsored (RGB)',
        },
        'Anonymous Sudan': {
            'alias': 'AnonymousSudan',
            'origin': 'Sudan (Disputed)',
            'active_since': '2023',
            'type': 'Hacktivist',
        },
        'DarkSide': {
            'alias': 'DarkSide Ransomware',
            'origin': 'Eastern Europe',
            'active_since': '2020',
            'type': 'Cybercrime (Ransomware)',
        },
        'REvil': {
            'alias': 'Sodinokibi',
            'origin': 'Russia',
            'active_since': '2019',
            'type': 'Cybercrime (Ransomware)',
        }
    }
    
    # Calculate threat levels dynamically
    for idx, row in actor_stats.iterrows():
        actor_name = row['actor']
        if actor_name not in actor_profiles:
            actor_profiles[actor_name] = {
                'alias': 'Unknown',
                'origin': 'Unknown',
                'active_since': 'Unknown',
                'type': 'Unclassified',
            }
    
    # Search and filters
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        search_term = st.text_input("Search Threat Actors", placeholder="Search by name, origin, or type...")
    with col2:
        threat_filter = st.selectbox("Threat Level", ["All", "Critical", "High"])
    with col3:
        sort_by = st.selectbox("Sort By", ["Total Attacks", "High Severity", "Alphabetical"])
    with col4:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("View All Actors" if not st.session_state.show_all_actors else "Show Top 12", use_container_width=True):
            st.session_state.show_all_actors = not st.session_state.show_all_actors
            st.rerun()
    
    # Apply filters
    filtered_stats = actor_stats.copy()
    if search_term:
        filtered_stats = filtered_stats[filtered_stats['actor'].str.contains(search_term, case=False, na=False)]
    
    # Calculate threat levels for filtering
    filtered_stats['threat_level'] = filtered_stats.apply(
        lambda row: determine_threat_level(
            row['actor'],
            row['total_attacks'],
            row['high_severity'],
            row['countries'],
            row['sectors'],
            actor_profiles.get(row['actor'], {}).get('type', 'Unknown')
        ),
        axis=1
    )
    
    # Filter by threat level
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
    
    # Display actor cards in grid
    actors_to_display = filtered_stats.head(num_to_show)
    
    # Create 4 columns per row for square grid
    num_cols = 4
    num_actors = len(actors_to_display)
    
    for i in range(0, num_actors, num_cols):
        cols = st.columns(num_cols)
        
        for j in range(num_cols):
            if i + j < num_actors:
                row = actors_to_display.iloc[i + j]
                actor_name = row['actor']
                profile = actor_profiles.get(actor_name, {
                    'alias': 'Unknown',
                    'origin': 'Unknown',
                    'type': 'Unclassified',
                    'active_since': 'Unknown'
                })
                
                threat_level = row['threat_level']
                threat_level_class = 'threat-critical' if threat_level == 'Critical' else 'threat-high'
                
                with cols[j]:
                    # Create card HTML
                    st.markdown(f"""
                    <div class="actor-card-container">
                        <span class="threat-badge {threat_level_class}">{threat_level}</span>
                        
                        <h3 class="actor-name-text">{actor_name}</h3>
                        <div class="actor-alias">{profile['alias']}</div>
                        
                        <div class="actor-info">
                            <div class="info-row">
                                <span class="info-label">Origin:</span>
                                <span>{profile['origin']}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">Type:</span>
                                <span>{profile['type']}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">Active:</span>
                                <span>Since {profile['active_since']}</span>
                            </div>
                        </div>
                        
                        <div class="actor-stats-grid">
                            <div class="stat-box">
                                <div class="stat-value">{int(row['total_attacks'])}</div>
                                <div class="stat-label">Attacks</div>
                            </div>
                            <div class="stat-box">
                                <div class="stat-value">{int(row['countries'])}</div>
                                <div class="stat-label">Countries</div>
                            </div>
                            <div class="stat-box">
                                <div class="stat-value">{int(row['sectors'])}</div>
                                <div class="stat-label">Sectors</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # View Profile button
                    if st.button("View Profile", key=f"btn_{actor_name}", use_container_width=True):
                        st.session_state.selected_actor = actor_name
                        st.query_params["actor"] = actor_name
                        st.switch_page("pages/2_📋_Actor_Profile.py")
    
    # Show count of displayed actors
    st.markdown("---")
    if st.session_state.show_all_actors:
        st.info(f"Showing all {num_actors} threat actors")
    else:
        st.info(f"Showing top {num_to_show} of {len(filtered_stats)} threat actors. Click 'View All Actors' to see more.")
    
else:
    st.info("No threat actor data available. Please load incidents data.")

# Summary statistics
if len(df) > 0:
    st.markdown("---")
    st.subheader("Threat Actor Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Threat Actors", len(actor_stats))
    with col2:
        critical_count = sum(1 for _, row in actor_stats.iterrows() 
                            if determine_threat_level(
                                row['actor'], 
                                row['total_attacks'], 
                                row['high_severity'], 
                                row['countries'], 
                                row['sectors'],
                                actor_profiles.get(row['actor'], {}).get('type', 'Unknown')
                            ) == 'Critical')
        st.metric("Critical Threat Actors", critical_count)
    with col3:
        st.metric("Total Attacks Tracked", int(actor_stats['total_attacks'].sum()))
    with col4:
        st.metric("High Severity Attacks", int(actor_stats['high_severity'].sum()))
