import streamlit as st
from datetime import datetime, timedelta
import feedparser
from dateutil import parser as date_parser
import re

CYHAWK_RED = "#C41E3A"
CYHAWK_RED_DARK = "#9A1529"

def get_theme_config():
    """Get theme configuration"""
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'
    
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

def apply_trending_attacks_css():
    """Apply CSS styles for trending attacks section"""
    C = get_theme_config()
    
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* Trending Attacks Section */
    .trending-section {{
        margin: 2rem 0;
    }}

    .trending-header {{
        background: linear-gradient(135deg, {C['accent']} 0%, {CYHAWK_RED_DARK} 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 16px rgba(196, 30, 58, 0.3);
    }}

    .trending-header h2 {{
        color: white;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }}

    .trending-header p {{
        color: rgba(255, 255, 255, 0.9);
        font-size: 1rem;
        margin-top: 0.5rem;
    }}

    .attacks-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
        gap: 1.5rem;
        margin-top: 1.5rem;
    }}

    .attack-card {{
        background: {C['card']};
        border: 2px solid {C['border']};
        border-radius: 12px;
        padding: 1.5rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }}

    .attack-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(196, 30, 58, 0.25);
        border-color: {C['accent']};
    }}

    .attack-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, {C['accent']} 0%, {CYHAWK_RED_DARK} 100%);
    }}

    .rank-badge {{
        position: absolute;
        top: 1rem;
        right: 1rem;
        color: white;
        font-size: 1.2rem;
        font-weight: 800;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    .attack-category {{
        display: inline-block;
        padding: 0.3rem 0.8rem;
        background: rgba(196, 30, 58, 0.15);
        color: {C['accent']};
        border-radius: 16px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }}

    .attack-title {{
        font-size: 1.1rem;
        font-weight: 700;
        color: {C['text']};
        margin: 0.8rem 0;
        line-height: 1.3;
        padding-right: 3rem;
    }}

    .attack-desc {{
        font-size: 0.9rem;
        color: {C['text_secondary']};
        line-height: 1.6;
        margin: 0.8rem 0;
    }}

    .attack-meta {{
        display: flex;
        gap: 1rem;
        padding-top: 1rem;
        border-top: 1px solid {C['border']};
        font-size: 0.85rem;
        color: {C['text_muted']};
        flex-wrap: wrap;
    }}

    .read-more {{
        display: inline-block;
        color: {C['accent']};
        font-weight: 600;
        text-decoration: none;
        margin-top: 0.8rem;
        padding: 0.6rem 1.2rem;
        background: rgba(196, 30, 58, 0.1);
        border-radius: 6px;
        transition: all 0.3s ease;
    }}

    .read-more:hover {{
        background: {C['accent']};
        color: white;
    }}

    @media (max-width: 768px) {{
        .attacks-grid {{
            grid-template-columns: 1fr;
        }}
        
        .trending-header h2 {{
            font-size: 1.5rem;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)

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
            "description": "A coordinated distributed denial-of-service attack affecting multiple banks across West Africa has been attributed to Anonymous Sudan. The attacks disrupted online banking services for over 48 hours.",
            "category": "Breaking News",
            "date": "2d ago",
            "read_time": "8 min",
            "url": "https://cyhawk-africa.com/blog",
            "source": "CyHawk Africa"
        },
        {
            "rank": 2,
            "title": "APT28 Targets Nigerian Government Infrastructure",
            "description": "Russian state-sponsored threat actor APT28 has been linked to an ongoing sophisticated spear-phishing campaign targeting Nigerian government officials and infrastructure operators.",
            "category": "APT Analysis",
            "date": "3d ago",
            "read_time": "6 min",
            "url": "https://cyhawk-africa.com/blog",
            "source": "CyHawk Africa"
        },
        {
            "rank": 3,
            "title": "REvil Ransomware Cripples Kenya Healthcare Network",
            "description": "A REvil ransomware attack on Kenya's largest hospital network has severely disrupted patient care and compromised sensitive medical records.",
            "category": "Ransomware",
            "date": "1w ago",
            "read_time": "5 min",
            "url": "https://cyhawk-africa.com/blog",
            "source": "CyHawk Africa"
        }
    ]

def render_trending_attacks_section():
    """Render the trending attacks section (use this in your main dashboard)"""
    apply_trending_attacks_css()
    
    st.markdown("""
    <div class="trending-section">
        <div class="trending-header">
            <h2>Top 3 Trending Cyber Attacks</h2>
            <p>Real-time threat intelligence from across Africa</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    attacks = load_top_attacks_from_rss()
    
    st.markdown('<div class="attacks-grid">', unsafe_allow_html=True)
    
    for attack in attacks:
        rank_color = "#FFD700" if attack['rank'] == 1 else "#C0C0C0" if attack['rank'] == 2 else "#CD7F32"
        
        st.markdown(f"""
        <div class="attack-card">
            <div class="rank-badge" style="background: {rank_color};">
                {attack['rank']}
            </div>
            
            <div class="attack-category">{attack['category']}</div>
            
            <h3 class="attack-title">{attack['title']}</h3>
            
            <p class="attack-desc">{attack['description']}</p>
            
            <div class="attack-meta">
                <span><strong>Published:</strong> {attack['date']}</span>
                <span><strong>Read:</strong> {attack['read_time']}</span>
            </div>
            
            <a href="{attack['url']}" target="_blank" class="read-more">
                Read Full Article →
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# If running as standalone page
if __name__ == "__main__":
    st.set_page_config(
        page_title="Top 3 Trending Attacks | CyHawk Africa",
        page_icon="🔒",
        layout="wide"
    )
    render_trending_attacks_section()
