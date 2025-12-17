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
        page_icon="🔒",
        layout="wide"
    )
    add_logo_and_branding()
except ImportError:
    st.set_page_config(
        page_title="Top 3 Trending Attacks | CyHawk Africa",
        page_icon="🔒",
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

# CSS Styles
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {{
    font-family: 'Inter', sans-serif;
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

.main {{
    background-color: {C['bg']};
    padding: 2rem;
}}

.stApp {{
    background: {C['bg']};
}}

/* Header Section */
.dashboard-header {{
    background: linear-gradient(135deg, {C['accent']} 0%, {CYHAWK_RED_DARK} 100%);
    padding: 3rem 2rem;
    border-radius: 16px;
    margin-bottom: 3rem;
    text-align: center;
    box-shadow: 0 8px 32px rgba(196, 30, 58, 0.3);
}}

.header-title {{
    color: white;
    font-size: 3rem;
    font-weight: 800;
    margin-bottom: 0.5rem;
    letter-spacing: -0.5px;
}}

.header-subtitle {{
    color: rgba(255, 255, 255, 0.95);
    font-size: 1.2rem;
    font-weight: 400;
    margin-top: 0.5rem;
}}

.last-updated {{
    color: rgba(255, 255, 255, 0.8);
    font-size: 0.9rem;
    margin-top: 1rem;
    font-weight: 500;
}}

/* Attack Cards Container */
.attacks-container {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 2rem;
    margin-top: 2rem;
    margin-bottom: 3rem;
}}

/* Individual Attack Card */
.attack-card {{
    background: {C['card']};
    border: 2px solid {C['border']};
    border-radius: 16px;
    padding: 2rem;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    position: relative;
    overflow: hidden;
    aspect-ratio: 1;
    display: flex;
    flex-direction: column;
    text-decoration: none;
}}

.attack-card:hover {{
    transform: translateY(-8px);
    box-shadow: 0 16px 40px rgba(196, 30, 58, 0.3);
    border-color: {C['accent']};
}}

.attack-card::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, {C['accent']} 0%, {CYHAWK_RED_DARK} 100%);
}}

/* Rank Badge */
.rank-badge {{
    position: absolute;
    top: 1.5rem;
    right: 1.5rem;
    color: white;
    font-size: 1.5rem;
    font-weight: 800;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}}

/* Category Badge */
.category-badge {{
    display: inline-block;
    padding: 0.4rem 1rem;
    background: rgba(196, 30, 58, 0.15);
    color: {C['accent']};
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 1rem;
}}

/* Attack Title */
.attack-title {{
    font-size: 1.4rem;
    font-weight: 700;
    color: {C['text']};
    margin: 1rem 0;
    line-height: 1.4;
    padding-right: 4rem;
    flex-grow: 0;
}}

/* Attack Description */
.attack-description {{
    font-size: 1rem;
    color: {C['text_secondary']};
    line-height: 1.7;
    margin: 1rem 0 1.5rem 0;
    flex-grow: 1;
}}

/* Meta Information */
.attack-meta {{
    display: flex;
    align-items: center;
    gap: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid {C['border']};
    font-size: 0.9rem;
    color: {C['text_muted']};
    flex-wrap: wrap;
    margin-top: auto;
}}

.meta-item {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
}}

.meta-label {{
    font-weight: 600;
}}

/* Read More Link */
.read-more-link {{
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    color: {C['accent']};
    font-weight: 600;
    text-decoration: none;
    margin-top: 1rem;
    padding: 0.75rem 1.5rem;
    background: rgba(196, 30, 58, 0.1);
    border-radius: 8px;
    transition: all 0.3s ease;
    text-align: center;
    justify-content: center;
}}

.read-more-link:hover {{
    background: {C['accent']};
    color: white;
    transform: translateX(4px);
}}

/* Stats Section */
.stats-container {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-top: 3rem;
    padding: 2rem;
    background: {C['card']};
    border-radius: 16px;
    border: 1px solid {C['border']};
}}

.stat-box {{
    text-align: center;
    padding: 1rem;
}}

.stat-value {{
    font-size: 2.5rem;
    font-weight: 800;
    color: {C['accent']};
    line-height: 1;
}}

.stat-label {{
    font-size: 0.9rem;
    color: {C['text_secondary']};
    margin-top: 0.5rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* Footer CTA */
.footer-cta {{
    text-align: center;
    padding: 2rem;
    margin-top: 3rem;
    background: {C['bg_secondary']};
    border-radius: 16px;
    border: 1px solid {C['border']};
}}

.footer-cta-text {{
    font-size: 1.1rem;
    color: {C['text']};
    font-weight: 600;
    margin-bottom: 1rem;
}}

.footer-cta-link {{
    color: {C['accent']};
    text-decoration: none;
    font-weight: 700;
}}

.footer-cta-link:hover {{
    text-decoration: underline;
}}

/* Responsive Design */
@media (max-width: 1200px) {{
    .attacks-container {{
        grid-template-columns: repeat(2, 1fr);
    }}
}}

@media (max-width: 768px) {{
    .header-title {{
        font-size: 2rem;
    }}
    
    .header-subtitle {{
        font-size: 1rem;
    }}
    
    .attacks-container {{
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }}
    
    .attack-title {{
        font-size: 1.2rem;
        padding-right: 3rem;
    }}
    
    .rank-badge {{
        width: 40px;
        height: 40px;
        font-size: 1.2rem;
        top: 1rem;
        right: 1rem;
    }}
    
    .stats-container {{
        grid-template-columns: repeat(2, 1fr);
    }}
}}

@media (max-width: 480px) {{
    .stats-container {{
        grid-template-columns: 1fr;
    }}
}}
</style>
""", unsafe_allow_html=True)

# Load blog posts from RSS feed
@st.cache_data(ttl=1800)  # Cache for 30 minutes
def load_top_attacks_from_rss():
    """Load top 3 trending attacks from CyHawk Africa RSS feed"""
    try:
        RSS_FEED_URL = "https://cyhawk-africa.com/feed/"
        
        # Parse RSS feed
        feed = feedparser.parse(RSS_FEED_URL)
        
        # Check if feed was parsed successfully
        if feed.bozo or not feed.entries:
            st.warning("RSS feed error. Displaying sample data.")
            return get_sample_attacks()
        
        attacks = []
        for idx, entry in enumerate(feed.entries[:3]):  # Get only top 3
            # Calculate relative time
            try:
                pub_date = date_parser.parse(entry.published)
                time_diff = datetime.now(pub_date.tzinfo) - pub_date
                
                if time_diff.days == 0:
                    if time_diff.seconds < 3600:
                        minutes = time_diff.seconds // 60
                        date_str = f"{minutes} minutes ago" if minutes > 1 else "Just now"
                    else:
                        hours = time_diff.seconds // 3600
                        date_str = f"{hours} hours ago"
                elif time_diff.days == 1:
                    date_str = "Yesterday"
                elif time_diff.days < 7:
                    date_str = f"{time_diff.days} days ago"
                elif time_diff.days < 30:
                    weeks = time_diff.days // 7
                    date_str = f"{weeks} weeks ago" if weeks > 1 else "1 week ago"
                else:
                    months = time_diff.days // 30
                    date_str = f"{months} months ago" if months > 1 else "1 month ago"
            except Exception as e:
                date_str = "Recently"
            
            # Extract category (from tags or default)
            category = "Threat Intelligence"
            if hasattr(entry, 'tags') and entry.tags:
                category = entry.tags[0].term
            elif hasattr(entry, 'category'):
                category = entry.category
            
            # Get excerpt and clean HTML
            excerpt = entry.get('summary', entry.get('description', ''))
            
            # Remove HTML tags
            excerpt = re.sub('<[^<]+?>', '', excerpt)
            
            # Clean up whitespace
            excerpt = ' '.join(excerpt.split())
            
            # Truncate to reasonable length
            if len(excerpt) > 200:
                excerpt = excerpt[:197] + '...'
            
            # Estimate read time based on content length
            try:
                content_length = len(entry.get('content', [{}])[0].get('value', excerpt))
                word_count = content_length // 5  # Rough estimate
                read_time = max(3, word_count // 200)  # ~200 words per minute
            except:
                word_count = len(excerpt.split()) * 5
                read_time = max(3, word_count // 200)
            
            attacks.append({
                "rank": idx + 1,
                "title": entry.title,
                "description": excerpt,
                "category": category,
                "date": date_str,
                "read_time": f"{read_time} min read",
                "url": entry.link,
                "source": entry.get('author', 'CyHawk Africa')
            })
        
        return attacks
        
    except Exception as e:
        st.error(f"Error loading RSS feed: {str(e)}")
        return get_sample_attacks()

def get_sample_attacks():
    """Fallback sample attacks if RSS feed fails"""
    return [
        {
            "rank": 1,
            "title": "Massive DDoS Campaign Targets African Financial Institutions",
            "description": "A coordinated distributed denial-of-service attack affecting multiple banks across West Africa has been attributed to the threat actor group Anonymous Sudan. The attacks successfully disrupted online banking services for over 48 hours, affecting millions of customers.",
            "category": "Breaking News",
            "date": "2 days ago",
            "read_time": "8 min read",
            "url": "https://cyhawk-africa.com/blog",
            "source": "CyHawk Africa"
        },
        {
            "rank": 2,
            "title": "APT28 Launches Sophisticated Phishing Campaign Against Nigerian Government",
            "description": "Russian state-sponsored threat actor APT28 (Fancy Bear) has been linked to an ongoing sophisticated spear-phishing campaign targeting Nigerian government officials and infrastructure operators. The campaign leverages weaponized documents and credential harvesting techniques.",
            "category": "APT Analysis",
            "date": "3 days ago",
            "read_time": "6 min read",
            "url": "https://cyhawk-africa.com/blog",
            "source": "CyHawk Africa"
        },
        {
            "rank": 3,
            "title": "REvil Ransomware Cripples Kenya Healthcare Network",
            "description": "A ransomware group has listed a major Nigerian insurance company on their leak site, threatening to release sensitive customer data. The attackers are demanding a substantial ransom payment.",
            "category": "Ransomware",
            "date": "1 week ago",
            "read_time": "5 min read",
            "url": "https://cyhawk-africa.com/blog",
            "source": "CyHawk Africa"
        }
    ]

# Main Dashboard
def main():
    # Header
    current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    st.markdown(f"""
    <div class="dashboard-header">
        <h1 class="header-title">Top 3 Trending Cyber Attacks</h1>
        <p class="header-subtitle">Real-time threat intelligence from across Africa</p>
        <p class="last-updated">Last Updated: {current_time}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load attacks
    with st.spinner("Loading latest threat intelligence..."):
        attacks = load_top_attacks_from_rss()
    
    # Display attacks in a single HTML block (this ensures proper rendering)
    rank_colors = {1: "#FFD700", 2: "#C0C0C0", 3: "#CD7F32"}
    
    attacks_html = '<div class="attacks-container">'
    
    for attack in attacks:
        rank_color = rank_colors.get(attack['rank'], "#CD7F32")
        
        attacks_html += f"""
        <a href="{attack['url']}" target="_blank" class="attack-card">
            <div class="rank-badge" style="background: {rank_color}; box-shadow: 0 4px 12px {rank_color}40;">
                {attack['rank']}
            </div>
            
            <div class="category-badge">{attack['category']}</div>
            
            <h2 class="attack-title">{attack['title']}</h2>
            
            <p class="attack-description">{attack['description']}</p>
            
            <div class="attack-meta">
                <div class="meta-item">
                    <span class="meta-label">Published:</span>
                    <span>{attack['date']}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Read Time:</span>
                    <span>{attack['read_time']}</span>
                </div>
            </div>
            
            <div class="read-more-link">
                Read Full Article →
            </div>
        </a>
        """
    
    attacks_html += '</div>'
    
    st.markdown(attacks_html, unsafe_allow_html=True)
    
    # Statistics Section
    total_attacks = len(attacks)
    categories = len(set(attack['category'] for attack in attacks))
    
    st.markdown(f"""
    <div class="stats-container">
        <div class="stat-box">
            <div class="stat-value">{total_attacks}</div>
            <div class="stat-label">Trending Attacks</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{categories}</div>
            <div class="stat-label">Threat Categories</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">24/7</div>
            <div class="stat-label">Monitoring</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">Real-Time</div>
            <div class="stat-label">Updates</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer CTA
    st.markdown("""
    <div class="footer-cta">
        <p class="footer-cta-text">
            Stay ahead of cyber threats in Africa
        </p>
        <p>
            Visit <a href="https://cyhawk-africa.com/blog" target="_blank" class="footer-cta-link">CyHawk Africa Blog</a> 
            for comprehensive threat intelligence and security research
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
