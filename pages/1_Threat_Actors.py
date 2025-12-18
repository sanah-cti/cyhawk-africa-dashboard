import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests

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

# -------------------------------------------------------------------
# CSS STYLES - DARK/LIGHT MODE ADAPTIVE
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

/* Actor Cards - Adaptive Colors */
.actor-card {{
    background: var(--secondary-background-color);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.5rem;
    height: 100%;
    transition: all 0.3s ease;
    position: relative;
}}

.actor-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(196, 30, 58, 0.2);
    border-color: {CYHAWK_RED};
}}

.threat-badge {{
    position: absolute;
    top: 1rem;
    right: 1rem;
    padding: 0.35rem 0.8rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

.threat-critical {{
    background: rgba(220, 38, 38, 0.15);
    color: #DC2626;
    border: 1px solid #DC2626;
}}

.threat-high {{
    background: rgba(249, 115, 22, 0.15);
    color: #F97316;
    border: 1px solid #F97316;
}}

.actor-name {{
    font-size: 1.4rem;
    font-weight: 700;
    margin-bottom: 0.8rem;
    color: var(--text-color);
}}

.actor-info {{
    margin: 0.6rem 0;
    font-size: 0.9rem;
    color: var(--text-color);
    opacity: 0.8;
}}

.actor-info strong {{
    opacity: 1;
    font-weight: 600;
}}

.stat-row {{
    display: flex;
    justify-content: space-between;
    margin-top: 1.2rem;
    padding-top: 1.2rem;
    border-top: 1px solid var(--border-color);
}}

.stat-item {{
    text-align: center;
    flex: 1;
}}

.stat-label {{
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-color);
    opacity: 0.6;
    margin-bottom: 0.3rem;
}}

.stat-value {{
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text-color);
}}

.view-profile-btn {{
    margin-top: 1.2rem;
    width: 100%;
    background: {CYHAWK_RED};
    color: white;
    padding: 0.75rem;
    border-radius: 8px;
    text-align: center;
    text-decoration: none;
    font-weight: 600;
    display: block;
    transition: all 0.2s ease;
}}

.view-profile-btn:hover {{
    background: {CYHAWK_RED_DARK};
    text-decoration: none;
    color: white;
}}

/* Ensure proper spacing */
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
# DATA LOADING
# -------------------------------------------------------------------
@st.cache_data
def load_data():
    if os.path.exists("data/incidents.csv"):
        df = pd.read_csv("data/incidents.csv")
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
        return df
    return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner=False)
def check_ransomware_live(actor_name):
    """Quick check if actor is in ransomware.live"""
    try:
        base = "https://api.ransomware.live"
        actor_normalized = actor_name.lower().replace(' ', '').replace('-', '').replace('_', '')
        
        # Check recent victims
        response = requests.get(f"{base}/recentvictims", timeout=5)
        if response.status_code == 200:
            victims = response.json()
            name_variants = [
                actor_name.lower(),
                actor_name.replace(' ', '').lower(),
                actor_name.replace(' ', '-').lower(),
            ]
            
            for victim in victims:
                group_name = victim.get('group_name', '').lower()
                if any(variant in group_name or group_name in variant for variant in name_variants):
                    return True
        return False
    except:
        return False

# -------------------------------------------------------------------
# CLASSIFICATION FUNCTION (SAME AS ACTOR PROFILE PAGE)
# -------------------------------------------------------------------
def classify_threat_actor_type(actor_name, actor_df):
    """
    Classify threat actor using same logic as Actor Profile page
    Priority: incident threat_type > ransomware.live > name patterns > default
    """
    actor_lower = actor_name.lower()
    
    # STEP 1: Check incident data first
    if not actor_df.empty and 'threat_type' in actor_df.columns:
        threat_types = actor_df['threat_type'].str.lower().fillna('')
        total = len(actor_df)
        
        ransomware_count = threat_types.str.contains('ransomware|ransom|encrypt', case=False, na=False).sum()
        database_count = threat_types.str.contains('database|breach|leak|dump|data theft|data leak|exfiltration', case=False, na=False).sum()
        iab_count = threat_types.str.contains('access|credential|exploit|vulnerability|source code|rdp|vpn|ssh|initial access', case=False, na=False).sum()
        ddos_count = threat_types.str.contains('ddos|denial of service|dos attack', case=False, na=False).sum()
        defacement_count = threat_types.str.contains('defacement|deface|website', case=False, na=False).sum()
        
        threshold = total * 0.3
        
        if ransomware_count > threshold:
            return "Ransomware"
        if database_count > threshold:
            return "Database Breach"
        if iab_count > threshold:
            return "Initial Access Broker (IAB)"
        if (ddos_count + defacement_count) > threshold:
            return "Hacktivist"
        
        # Use highest count if no threshold met
        threat_counts = {
            'Ransomware': ransomware_count,
            'Database Breach': database_count,
            'Initial Access Broker (IAB)': iab_count,
            'Hacktivist': ddos_count + defacement_count
        }
        max_type = max(threat_counts, key=threat_counts.get)
        if threat_counts[max_type] > 0:
            return max_type
    
    # STEP 2: Check ransomware.live
    if check_ransomware_live(actor_name):
        return "Ransomware"
    
    # STEP 3: Check name patterns
    ransomware_keywords = ['ransomware', 'lockbit', 'revil', 'darkside', 'conti', 'maze', 'blackcat', 
                          'alphv', 'ryuk', 'nightspire', 'play', 'royal', 'medusa', 'funksec', 'ransom']
    if any(kw in actor_lower for kw in ransomware_keywords):
        return "Ransomware"
    
    iab_keywords = ['bigbrother', 'broker', 'access', 'iab', 'initial']
    if any(kw in actor_lower for kw in iab_keywords):
        return "Initial Access Broker (IAB)"
    
    db_keywords = ['b4bayega', 'database', 'breach', 'leak', 'dump', 'shinyh']
    if any(kw in actor_lower for kw in db_keywords):
        return "Database Breach"
    
    # STEP 4: Default
    return "Hacktivist"

def determine_origin(actor_name, actor_df):
    """Determine likely origin based on targeting patterns"""
    if actor_df.empty:
        return "Unknown"
    
    # Check for known origins from name
    origin_mapping = {
        'sudan': 'Sudan',
        'anonymous sudan': 'Sudan (Disputed)',
        'apt28': 'Russia',
        'fancy bear': 'Russia',
        'lazarus': 'North Korea',
        'kimsuky': 'North Korea',
        'china': 'China',
        'iran': 'Iran',
    }
    
    actor_lower = actor_name.lower()
    for keyword, origin in origin_mapping.items():
        if keyword in actor_lower:
            return origin
    
    # Infer from targeting (if heavily focused on one region, likely from elsewhere)
    top_country = actor_df['country'].value_counts().index[0] if not actor_df.empty else None
    if top_country and len(actor_df[actor_df['country'] == top_country]) > len(actor_df) * 0.7:
        return f"Likely External (targets {top_country})"
    
    return "Unknown"

def determine_active_since(actor_df):
    """Determine when actor became active"""
    if actor_df.empty:
        return "Unknown"
    
    first_seen = actor_df['date'].min()
    if pd.notna(first_seen):
        return first_seen.strftime('%Y')
    return "Unknown"

# -------------------------------------------------------------------
# THREAT LEVEL DETERMINATION
# -------------------------------------------------------------------
def determine_threat_level(actor_name, total_attacks, countries, sectors, actor_type):
    """Determine threat level based on multiple factors"""
    # Ransomware is always Critical
    if actor_type == "Ransomware":
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
    
    # IAB and Database Breach can be Critical based on volume
    if actor_type in ["Initial Access Broker (IAB)", "Database Breach"] and total_attacks > 20:
        return 'Critical'
    
    return 'High'

# -------------------------------------------------------------------
# LOAD AND PROCESS DATA
# -------------------------------------------------------------------
df = load_data()

if not df.empty:
    # Calculate basic stats
    stats = df.groupby("actor").agg(
        attacks=("date", "count"),
        countries=("country", "nunique"),
        sectors=("sector", "nunique")
    ).reset_index()
    
    # Enrich with auto-determined data
    enriched_data = []
    for _, row in stats.iterrows():
        actor_name = row['actor']
        actor_df = df[df['actor'] == actor_name]
        
        enriched_data.append({
            'actor': actor_name,
            'attacks': row['attacks'],
            'countries': row['countries'],
            'sectors': row['sectors'],
            'type': classify_threat_actor_type(actor_name, actor_df),
            'origin': determine_origin(actor_name, actor_df),
            'active': f"Since {determine_active_since(actor_df)}"
        })
    
    stats = pd.DataFrame(enriched_data)
    
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
else:
    stats = pd.DataFrame(columns=["actor", "attacks", "countries", "sectors", "type", "origin", "active", "threat_level"])

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

# Limit display
if not st.session_state.show_all_actors:
    filtered = filtered.head(12)

# -------------------------------------------------------------------
# DISPLAY ACTOR CARDS
# -------------------------------------------------------------------
if not filtered.empty:
    # Create grid layout (4 columns)
    num_cols = 4
    rows = [filtered.iloc[i:i+num_cols] for i in range(0, len(filtered), num_cols)]
    
    for row_data in rows:
        cols = st.columns(num_cols)
        for idx, (_, actor) in enumerate(row_data.iterrows()):
            with cols[idx]:
                threat_badge_class = "threat-critical" if actor['threat_level'] == 'Critical' else "threat-high"
                
                card_html = f"""
                <div class="actor-card">
                    <div class="threat-badge {threat_badge_class}">{actor['threat_level'].upper()}</div>
                    
                    <div class="actor-name">{actor['actor']}</div>
                    
                    <div class="actor-info">
                        <strong>Origin:</strong> {actor['origin']}<br>
                        <strong>Type:</strong> {actor['type']}<br>
                        <strong>Active:</strong> {actor['active']}
                    </div>
                    
                    <div class="stat-row">
                        <div class="stat-item">
                            <div class="stat-label">Attacks</div>
                            <div class="stat-value">{actor['attacks']}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Countries</div>
                            <div class="stat-value">{actor['countries']}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Sectors</div>
                            <div class="stat-value">{actor['sectors']}</div>
                        </div>
                    </div>
                    
                    <a href="/Actor_Profile?actor={actor['actor']}" class="view-profile-btn" target="_self">
                        View Profile
                    </a>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                st.markdown("")  # Spacing
else:
    st.info("No threat actors found matching your filters.")
