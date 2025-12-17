import streamlit as st
from datetime import datetime, timedelta
import feedparser
from dateutil import parser as date_parser
import re

# Import navigation utilities
try:
    from navigation_utils import add_logo_and_branding, set_page_config as custom_set_page_config
    custom_set_page_config(
        page_title="Top 3 Trending Attacks | CyHawk Africa",
        page_icon="assets/favicon.ico",
        layout="wide"
    )
    add_logo_and_branding()
except ImportError:
    st.set_page_config(
        page_title="Top 3 Trending Attacks | CyHawk Africa",
        page_icon="assets/favicon.ico",
        layout="wide"
    )

# Theme
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

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
    }

C = theme_config()

# CSS Styles - Simplified
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.main {{
    background-color: {C['bg']};
}}

.stApp {{
    background: {C['bg']};
}}

/* Header */
.trending-header {{
    background: linear-gradient(135deg, #C41E3A 0%, {CYHAWK_RED_DARK} 100%);
    padding: 3rem 2rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    text-align: center;
    box-shadow: 0 8px 32px rgba(196, 30, 58, 0.3);
}}

.trending-title {{
    color: white;
    font-size: 3rem;
    font-weight: 800;
    margin: 0;
}}

.trending-subtitle {{
    color: rgba(255, 255, 255, 0.95);
    font-size: 1.2rem;
    margin-top: 0.5rem;
}}

.trending-updated {{
    color: rgba(255, 255, 255, 0.8);
    font-size: 0.9rem;
    margin-top: 1rem;
}}

/* Cards using Streamlit containers */
.stContainer > div {{
    background: {C['card']};
    border: 2px solid {C['border']};
    border-radius: 16px;
    padding: 2rem;
    transition: all 0.3s ease;
    position: relative;
    height: 100%;
    min-height: 400px;
}}

.stContainer > div:hover {{
    border-color: #C41E3A;
    box-shadow: 0 12px 32px rgba(196, 30, 58, 0.3);
}}

/* Hide Streamlit default styling */
.element-container {{
    margin-bottom: 0 !important;
}}

[data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {{
    gap: 0.5rem;
}}
</style>
""", unsafe_allow_html=True)

# Load blog posts from RSS feed
@st.cache_data(ttl=1800)
def load_top_attacks_from_rss():
    """Load top 3 trending attacks from CyHawk Africa RSS feed"""
    try:
        RSS_FEED_URL = "https://cyhawk-africa.com/feed/"
        feed = feedparser.parse(RSS_FEED_URL)
        
        if feed.bozo or not feed.entries:
            return get_sample_attacks()
        
        attacks = []
        for idx, entry in enumerate(feed.entries[:3]):
            try:
                pub_date = date_parser.parse(entry.published)
                time_diff = datetime.now(pub_date.tzinfo) - pub_date
                
                if time_diff.days == 0:
                    if time_diff.seconds < 3600:
                        minutes = time_diff.seconds // 60
                        date_str = f"{minutes} min ago" if minutes > 1 else "Just now"
                    else:
                        hours = time_diff.seconds // 3600
                        date_str = f"{hours}h ago"
                elif time_diff.days == 1:
                    date_str = "Yesterday"
                elif time_diff.days < 7:
                    date_str = f"{time_diff.days}d ago"
                else:
                    date_str = f"{time_diff.days // 7}w ago"
            except:
                date_str = "Recently"
            
            category = "Threat Intelligence"
            if hasattr(entry, 'tags') and entry.tags:
                category = entry.tags[0].term
            elif hasattr(entry, 'category'):
                category = entry.category
            
            excerpt = entry.get('summary', entry.get('description', ''))
            excerpt = re.sub('<[^<]+?>', '', excerpt)
            excerpt = ' '.join(excerpt.split())
            if len(excerpt) > 200:
                excerpt = excerpt[:197] + '...'
            
            try:
                content_length = len(entry.get('content', [{}])[0].get('value', excerpt))
                read_time = max(3, (content_length // 5) // 200)
            except:
                read_time = max(3, (len(excerpt.split()) * 5) // 200)
            
            attacks.append({
                "rank": idx + 1,
                "title": entry.title,
                "description": excerpt,
                "category": category,
                "date": date_str,
                "read_time": f"{read_time} min",
                "url": entry.link,
                "source": entry.get('author', 'CyHawk Africa')
            })
        
        return attacks
        
    except Exception as e:
        return get_sample_attacks()

def get_sample_attacks():
    """Fallback sample attacks"""
    return [
        {
            "rank": 1,
            "title": "Massive DDoS Campaign Targets African Financial Institutions",
            "description": "A coordinated distributed denial-of-service attack affecting multiple banks across West Africa has been attributed to the threat actor group Anonymous Sudan. The attacks successfully disrupted online banking services.",
            "category": "Breaking News",
            "date": "2d ago",
            "read_time": "8 min",
            "url": "https://cyhawk-africa.com/blog",
            "source": "CyHawk Africa"
        },
        {
            "rank": 2,
            "title": "APT28 Launches Sophisticated Phishing Campaign Against Nigerian Government",
            "description": "Russian state-sponsored threat actor APT28 has been linked to an ongoing sophisticated spear-phishing campaign targeting Nigerian government officials and infrastructure operators.",
            "category": "APT Analysis",
            "date": "3d ago",
            "read_time": "6 min",
            "url": "https://cyhawk-africa.com/blog",
            "source": "CyHawk Africa"
        },
        {
            "rank": 3,
            "title": "Ransomware Group Targets Nigerian Insurance Company",
            "description": "A ransomware group has listed a major Nigerian insurance company on their leak site, threatening to release sensitive customer data unless a ransom is paid.",
            "category": "Ransomware",
            "date": "1w ago",
            "read_time": "5 min",
            "url": "https://cyhawk-africa.com/blog",
            "source": "CyHawk Africa"
        }
    ]

# Main Dashboard
def main():
    # Header
    current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    st.markdown(f"""
    <div class="trending-header">
        <h1 class="trending-title">Top 3 Trending Cyber Attacks</h1>
        <p class="trending-subtitle">Real-time threat intelligence from across Africa</p>
        <p class="trending-updated">Last Updated: {current_time}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load attacks
    attacks = load_top_attacks_from_rss()
    
    # Display attacks using Streamlit columns
    cols = st.columns(3, gap="large")
    
    rank_colors = {1: "#FFD700", 2: "#C0C0C0", 3: "#CD7F32"}
    
    for idx, attack in enumerate(attacks):
        with cols[idx]:
            # Rank badge
            rank_color = rank_colors.get(attack['rank'], "#CD7F32")
            st.markdown(f"""
                <div style="position: absolute; top: 1.5rem; right: 1.5rem; 
                     background: {rank_color}; color: white; font-size: 1.5rem; 
                     font-weight: 800; width: 50px; height: 50px; border-radius: 50%; 
                     display: flex; align-items: center; justify-content: center;
                     box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                    {attack['rank']}
                </div>
            """, unsafe_allow_html=True)
            
            # Category badge
            st.markdown(f"""
                <div style="display: inline-block; padding: 0.4rem 1rem; 
                     background: rgba(196, 30, 58, 0.15); color: #C41E3A; 
                     border-radius: 20px; font-size: 0.75rem; font-weight: 700; 
                     text-transform: uppercase; margin-bottom: 1rem;">
                    {attack['category']}
                </div>
            """, unsafe_allow_html=True)
            
            # Title
            st.markdown(f"""
                <h2 style="font-size: 1.3rem; font-weight: 700; color: inherit; 
                     margin: 1rem 0; line-height: 1.4; padding-right: 3rem;">
                    {attack['title']}
                </h2>
            """, unsafe_allow_html=True)
            
            # Description
            st.markdown(f"""
                <p style="font-size: 0.95rem; color: rgba(128, 128, 128, 0.8); 
                     line-height: 1.6; margin: 1rem 0;">
                    {attack['description']}
                </p>
            """, unsafe_allow_html=True)
            
            # Spacer
            st.markdown("<div style='flex-grow: 1; min-height: 2rem;'></div>", unsafe_allow_html=True)
            
            # Meta info
            st.markdown(f"""
                <div style="display: flex; gap: 1rem; padding-top: 1rem; 
                     border-top: 1px solid {C['border']}; font-size: 0.85rem; 
                     color: rgba(128, 128, 128, 0.6); margin-bottom: 1rem;">
                    <span><strong>Published:</strong> {attack['date']}</span>
                    <span><strong>Read:</strong> {attack['read_time']}</span>
                </div>
            """, unsafe_allow_html=True)
            
            # Read more button
            st.link_button(
                "Read Full Article →",
                attack['url'],
                use_container_width=True,
                type="primary"
            )
    
    # Statistics
    st.markdown("---")
    stat_cols = st.columns(4)
    
    with stat_cols[0]:
        st.metric("Trending Attacks", len(attacks))
    with stat_cols[1]:
        categories = len(set(attack['category'] for attack in attacks))
        st.metric("Threat Categories", categories)
    with stat_cols[2]:
        st.metric("Monitoring", "24/7")
    with stat_cols[3]:
        st.metric("Updates", "Real-Time")
    
    # Footer
    st.markdown("---")
    st.info("💡 **Stay Updated:** Visit [cyhawk-africa.com/blog](https://cyhawk-africa.com/blog) for comprehensive threat intelligence and security research.")

if __name__ == "__main__":
    main()
