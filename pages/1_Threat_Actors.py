import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Import navigation utilities
try:
    from navigation_utils import add_logo_and_branding, set_page_config as custom_set_page_config
    custom_set_page_config(
        page_title="Threat Actor Intelligence | CyHawk Africa",
        page_icon="assets/favicon.ico",
        layout="wide"
    )
    add_logo_and_branding()
except ImportError:
    st.set_page_config(
        page_title="Threat Actor Intelligence | CyHawk Africa",
        page_icon="assets/favicon.ico",
        layout="wide"
    )

# -------------------------------------------------------------------
# BRANDING & THEME
# -------------------------------------------------------------------
CYHAWK_RED = "#C41E3A"
CYHAWK_RED_DARK = "#9A1529"

# Initialize view all state
if 'show_all_actors' not in st.session_state:
    st.session_state.show_all_actors = False

# Theme-aware colors based on Streamlit's theme
# Check if we're in dark mode (default) or light mode
def get_theme_colors():
    # Try to detect theme from query params or default to dark
    try:
        # Streamlit automatically handles this, but we provide fallback colors
        return {
            "bg": "var(--background-color)",
            "card": "var(--secondary-background-color)",
            "border": "var(--border-color)",
            "text": "var(--text-color)",
            "text_muted": "var(--text-secondary-color)"
        }
    except:
        # Fallback to dark theme colors
        return {
            "bg": "#0D1117",
            "card": "#161B22",
            "border": "#30363D",
            "text": "#E6EDF3",
            "text_muted": "#8B949E"
        }

# -------------------------------------------------------------------
# CSS STYLES
# -------------------------------------------------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
* {{ font-family: 'Inter', sans-serif; }}

.hero {{
    background: linear-gradient(135deg, {CYHAWK_RED} 0%, {CYHAWK_RED_DARK} 100%);
    padding: 3.5rem 2rem;
    border-radius: 14px;
    text-align: center;
    margin-bottom: 2.5rem;
    box-shadow: 0 8px 32px rgba(196, 30, 58, 0.3);
}}
.hero h1 {{
    color: #ffffff;
    font-size: 2.8rem;
    font-weight: 800;
    margin-bottom: 0.6rem;
    letter-spacing: -0.5px;
}}
.hero p {{
    color: rgba(255,255,255,0.95);
    font-size: 1.15rem;
    max-width: 720px;
    margin: 0 auto;
    line-height: 1.6;
}}

/* Square Card Containers */
.stContainer {{
    position: relative;
}}

[data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] {{
    gap: 1rem;
}}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# HEADER
# -------------------------------------------------------------------
st.markdown("""
<div class="hero">
    <h1>Threat Actor Intelligence</h1>
    <p>Comprehensive profiles of active threat actors targeting African organizations</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------------------
@st.cache_data
def load_data():
    if os.path.exists("data/incidents.csv"):
        df = pd.read_csv("data/incidents.csv")
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
        return df
    return pd.DataFrame()

df = load_data()

# -------------------------------------------------------------------
# FUNCTION TO DETERMINE THREAT LEVEL
# -------------------------------------------------------------------
def determine_threat_level(actor_name, total_attacks, countries, sectors, actor_type):
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

# -------------------------------------------------------------------
# ACTOR METRICS
# -------------------------------------------------------------------
if not df.empty:
    stats = df.groupby("actor").agg(
        attacks=("date", "count"),
        countries=("country", "nunique"),
        sectors=("sector", "nunique")
    ).reset_index()
else:
    stats = pd.DataFrame(columns=["actor", "attacks", "countries", "sectors"])

# -------------------------------------------------------------------
# ACTOR PROFILES (EXPANDED)
# -------------------------------------------------------------------
ACTOR_META = {
    "Keymous Plus": {"alias": "Unknown", "origin": "Unknown", "type": "Unclassified", "active": "Since Unknown"},
    "OurSec": {"alias": "Unknown", "origin": "Unknown", "type": "Unclassified", "active": "Since Unknown"},
    "Funksec": {"alias": "Unknown", "origin": "Unknown", "type": "Unclassified", "active": "Since Unknown"},
    "dark hell 07x": {"alias": "Unknown", "origin": "Unknown", "type": "Unclassified", "active": "Since Unknown"},
    "FireWire": {"alias": "Unknown", "origin": "Unknown", "type": "Unclassified", "active": "Since Unknown"},
    "Devman": {"alias": "Unknown", "origin": "Unknown", "type": "Unclassified", "active": "Since Unknown"},
    "SKYZZXPLOIT": {"alias": "Unknown", "origin": "Unknown", "type": "Unclassified", "active": "Since Unknown"},
    "hider_nex": {"alias": "Unknown", "origin": "Unknown", "type": "Unclassified", "active": "Since Unknown"},
    "Nightspire": {"alias": "Unknown", "origin": "Unknown", "type": "Unclassified", "active": "Since Unknown"},
    "KillSec": {"alias": "Unknown", "origin": "Unknown", "type": "Hacktivist", "active": "Since Unknown"},
    "GhostSec": {"alias": "Unknown", "origin": "Unknown", "type": "Hacktivist", "active": "Since Unknown"},
    "Anonymous Sudan": {"alias": "AnonymousSudan", "origin": "Sudan (Disputed)", "type": "Hacktivist", "active": "2023"},
    "APT28": {"alias": "Fancy Bear, Sofacy", "origin": "Russia", "type": "State-Sponsored (GRU)", "active": "2007"},
    "Lazarus Group": {"alias": "HIDDEN COBRA", "origin": "North Korea", "type": "State-Sponsored (RGB)", "active": "2009"},
    "DarkSide": {"alias": "DarkSide Ransomware", "origin": "Eastern Europe", "type": "Cybercrime (Ransomware)", "active": "2020"},
    "REvil": {"alias": "Sodinokibi", "origin": "Russia", "type": "Cybercrime (Ransomware)", "active": "2019"},
}

# Merge with stats
stats = stats.merge(
    pd.DataFrame.from_dict(ACTOR_META, orient="index").reset_index().rename(columns={"index": "actor"}),
    on="actor",
    how="left"
)

stats.fillna({
    "alias": "Unknown",
    "origin": "Unknown", 
    "type": "Unclassified", 
    "active": "Since Unknown"
}, inplace=True)

# Calculate threat levels
stats['threat_level'] = stats.apply(
    lambda row: determine_threat_level(
        row['actor'], 
        row['attacks'], 
        row['countries'], 
        row['sectors'],
        row['type']
    ), axis=1
)

# -------------------------------------------------------------------
# FILTER BAR
# -------------------------------------------------------------------
f1, f2, f3, f4 = st.columns([2.5, 1.2, 1.2, 1.4])

with f1:
    search = st.text_input("Search Threat Actors", placeholder="Search by name, origin, or type...")

with f2:
    threat_level = st.selectbox("Threat Level", ["All", "Critical", "High"])

with f3:
    sort_by = st.selectbox("Sort By", ["Total Attacks", "Alphabetical"])

with f4:
    view_all_btn = st.button(
        "View All Actors" if not st.session_state.show_all_actors else "Show Top 12",
        use_container_width=True,
        type="primary"
    )
    if view_all_btn:
        st.session_state.show_all_actors = not st.session_state.show_all_actors
        st.rerun()

# -------------------------------------------------------------------
# FILTER LOGIC
# -------------------------------------------------------------------
filtered = stats.copy()

if search:
    filtered = filtered[
        filtered["actor"].str.contains(search, case=False, na=False)
        | filtered["origin"].str.contains(search, case=False, na=False)
        | filtered["type"].str.contains(search, case=False, na=False)
    ]

if threat_level != "All":
    filtered = filtered[filtered["threat_level"] == threat_level]

if sort_by == "Total Attacks":
    filtered = filtered.sort_values("attacks", ascending=False)
else:
    filtered = filtered.sort_values("actor")

# Determine how many to show
num_to_show = len(filtered) if st.session_state.show_all_actors else min(12, len(filtered))
filtered = filtered.head(num_to_show)

# -------------------------------------------------------------------
# DISPLAY CARDS IN 4-COLUMN GRID
# -------------------------------------------------------------------
num_cols = 4
num_actors = len(filtered)

for i in range(0, num_actors, num_cols):
    cols = st.columns(num_cols, gap="medium")
    
    for j in range(num_cols):
        if i + j < num_actors:
            row = filtered.iloc[i + j]
            threat_badge_color = "#DA3633" if row['threat_level'] == 'Critical' else '#ff6b6b'
            
            with cols[j]:
                with st.container(border=True):
                    # Header with threat badge
                    st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                            <h3 style="margin: 0; font-size: 1.1rem; font-weight: 700; flex: 1; padding-right: 1rem;">
                                {row['actor']}
                            </h3>
                            <span style="background: {threat_badge_color}; color: white; padding: 0.25rem 0.6rem; 
                                  border-radius: 12px; font-size: 0.65rem; font-weight: 700; 
                                  text-transform: uppercase; white-space: nowrap;">
                                {row['threat_level']}
                            </span>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Alias
                    st.markdown(f"""
                        <p style="font-size: 0.8rem; opacity: 0.7;
                             font-style: italic; margin: 0 0 1rem 0;">
                            {row['alias']}
                        </p>
                    """, unsafe_allow_html=True)
                    
                    # Info
                    st.markdown(f"""
                        <div style="font-size: 0.85rem; opacity: 0.8;
                             margin-bottom: 1rem; line-height: 1.6;">
                            <div><strong>Origin:</strong> {row['origin']}</div>
                            <div><strong>Type:</strong> {row['type']}</div>
                            <div><strong>Active:</strong> {row['active']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Stats
                    stat_col1, stat_col2, stat_col3 = st.columns(3)
                    with stat_col1:
                        st.metric("Attacks", int(row['attacks']))
                    with stat_col2:
                        st.metric("Countries", int(row['countries']))
                    with stat_col3:
                        st.metric("Sectors", int(row['sectors']))
                    
                    # View Profile button
                    actor_url_safe = row['actor'].replace(' ', '%20')
                    st.markdown(f"""
                        <a href="/Actor_Profile?actor={actor_url_safe}" target="_blank" style="
                            display: block;
                            width: 100%;
                            padding: 0.5rem;
                            background: {CYHAWK_RED};
                            color: white;
                            text-align: center;
                            text-decoration: none;
                            border-radius: 6px;
                            font-weight: 600;
                            transition: all 0.3s ease;
                        " onmouseover="this.style.background='{CYHAWK_RED_DARK}'" 
                           onmouseout="this.style.background='{CYHAWK_RED}'">
                            View Profile
                        </a>
                    """, unsafe_allow_html=True)

# -------------------------------------------------------------------
# STATUS MESSAGE
# -------------------------------------------------------------------
st.markdown("---")
if st.session_state.show_all_actors:
    st.success(f"✅ Showing all {num_actors} threat actors")
else:
    st.info(f"ℹ️ Showing top {num_to_show} of {len(stats)} threat actors")

# -------------------------------------------------------------------
# SUMMARY STATS
# -------------------------------------------------------------------
if not stats.empty:
    st.markdown("---")
    st.subheader("Threat Actor Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Threat Actors", len(stats))
    
    with col2:
        critical_count = len(stats[stats['threat_level'] == 'Critical'])
        st.metric("Critical Threat Actors", critical_count)
    
    with col3:
        st.metric("Total Attacks Tracked", int(stats['attacks'].sum()))
    
    with col4:
        st.metric("Unique Countries", df['country'].nunique() if not df.empty else 0)
