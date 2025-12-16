import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

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
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown(f"""
    <div class="top-header">
        <div style="display:flex;align-items:center;gap:1rem">
            <img src="assets/cyhawk_logo.png" width="55">
            <div>
                <h2 style="margin:0;color:{C['text']}">CyHawk Africa</h2>
                <p style="margin:0;color:{C['muted']}">Cyber Threat Intelligence Platform</p>
            </div>
        </div>
        <div style="display:flex;gap:2rem">
            <div><strong style="color:{BRAND_RED}">Live</strong><br><small>Monitoring</small></div>
            <div><strong style="color:{BRAND_RED}">Africa</strong><br><small>Coverage</small></div>
            <div><strong style="color:{BRAND_RED}">24/7</strong><br><small>Visibility</small></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if st.button("🌙" if st.session_state.theme == "dark" else "☀️"):
        toggle_theme()
        st.rerun()

# --------------------------------------------------
# NOTICE (IMPORTANT)
# --------------------------------------------------
st.info(
    "This public dashboard shows **aggregated and non-sensitive visual insights only**. "
    "Operational threat intelligence data is restricted to authorized partners."
)

# --------------------------------------------------
# SYNTHETIC / AGGREGATED VISUALS ONLY
# --------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    fig = px.pie(
        names=["Ransomware", "Phishing", "DDoS", "Malware"],
        values=[35, 25, 20, 20],
        hole=0.5,
        template=C["template"]
    )
    fig.update_layout(title="Threat Categories (Aggregated)")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    fig = px.bar(
        x=["Finance", "Government", "Telecoms", "Healthcare"],
        y=[40, 30, 20, 10],
        template=C["template"]
    )
    fig.update_layout(title="Most Targeted Sectors (Index View)")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# TIMELINE (NO DATA)
# --------------------------------------------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    y=[12, 18, 14, 22, 19, 10, 8],
    mode="lines",
    fill="tozeroy"
))
fig.update_layout(
    title="Threat Activity Index (Abstracted)",
    template=C["template"],
    height=300
)
st.plotly_chart(fig, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown(f"""
<div style="text-align:center;color:{C['muted']};padding:2rem;border-top:1px solid {C['border']}">
CyHawk Africa © {datetime.now().year} — Public Intelligence Interface
</div>
""", unsafe_allow_html=True)
