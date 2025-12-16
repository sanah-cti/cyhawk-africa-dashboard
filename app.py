import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import io
import os

# -------------------------------------------------
# PAGE CONFIG (ICON FROM ASSETS)
# -------------------------------------------------
st.set_page_config(
    page_title="CyHawk Africa – Cyber Threat Intelligence",
    page_icon="assets/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "view_mode" not in st.session_state:
    st.session_state.view_mode = "Public"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

# -------------------------------------------------
# COLORS
# -------------------------------------------------
BRAND_RED = "#B91C1C"

def theme_colors():
    if st.session_state.theme == "dark":
        return {
            "bg": "#0a0e27",
            "card": "#141b3d",
            "border": "#1e2847",
            "text": "#ffffff",
            "muted": "#9aa0c7",
            "plotly": "plotly_dark"
        }
    return {
        "bg": "#f5f7fa",
        "card": "#ffffff",
        "border": "#e5e7eb",
        "text": "#1a1d29",
        "muted": "#6b7280",
        "plotly": "plotly_white"
    }

C = theme_colors()

# -------------------------------------------------
# CSS
# -------------------------------------------------
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
* {{ font-family: Inter, sans-serif; }}
.stApp {{ background-color: {C["bg"]}; }}
header, footer, #MainMenu {{ display: none; }}

.top-header {{
    background: {C["card"]};
    border-bottom: 1px solid {C["border"]};
    padding: 1.5rem 2rem;
    margin: -6rem -6rem 2rem -6rem;
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 1.5rem;
}}

.brand {{
    display: flex;
    align-items: center;
    gap: 1rem;
}}

.brand img {{
    height: 56px;
}}

.brand h1 {{
    margin: 0;
    color: {C["text"]};
    font-size: 1.6rem;
}}

.brand p {{
    margin: 0;
    color: {C["muted"]};
    font-size: 0.85rem;
}}

.stats {{
    display: flex;
    gap: 2rem;
    flex-wrap: wrap;
}}

.stat {{
    text-align: center;
}}

.stat strong {{
    color: {BRAND_RED};
    font-size: 1.6rem;
}}

.card {{
    background: {C["card"]};
    border: 1px solid {C["border"]};
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}}

[data-testid="stSidebar"] {{
    background: {C["card"]};
    border-right: 1px solid {C["border"]};
}}
</style>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------
# SAMPLE DATA
# -------------------------------------------------
def generate_sample_data():
    actors = ["Keymous Plus", "iFalcon", "APT28", "Anonymous Sudan", "DarkSide"]
    countries = ["Nigeria", "South Africa", "Kenya", "Egypt", "Ghana"]
    threats = ["DDoS", "Ransomware", "Phishing", "Data Breach"]
    sectors = ["Finance", "Government", "Telecoms", "Health"]
    severities = ["High", "Medium", "Low"]

    rows = []
    start = datetime(2025, 1, 1)

    for _ in range(200):
        rows.append({
            "date": start + timedelta(days=random.randint(0, 240)),
            "actor": random.choice(actors),
            "country": random.choice(countries),
            "threat_type": random.choice(threats),
            "sector": random.choice(sectors),
            "severity": random.choice(severities),
            "source": "OSINT"
        })

    return pd.DataFrame(rows)

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
@st.cache_data(ttl=300)
def load_data():
    path = "data/incidents.csv"
    if os.path.exists(path):
        df = pd.read_csv(path)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
    else:
        df = generate_sample_data()

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.strftime("%B")
    df["quarter"] = df["date"].dt.quarter
    return df

df = load_data()

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.markdown(
    f"""
<div class="top-header">
  <div class="brand">
    <a href="https://cyhawk-africa.com" target="_blank">
      <img src="assets/cyhawk_logo.png">
    </a>
    <div>
      <h1>CyHawk Africa</h1>
      <p>Cyber Threat Intelligence Platform</p>
    </div>
  </div>

  <div class="stats">
    <div class="stat"><strong>{len(df)}</strong><br>Threats</div>
    <div class="stat"><strong>{df.actor.nunique()}</strong><br>Actors</div>
    <div class="stat"><strong>{df.country.nunique()}</strong><br>Countries</div>
    <div class="stat"><strong>{len(df[df.severity=="High"])}</strong><br>High Risk</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:
    st.button("Toggle Theme", on_click=toggle_theme)

    st.markdown("### Access Mode")
    st.session_state.view_mode = st.radio(
        "",
        ["Public", "Internal"],
        index=0
    )

    st.markdown("### Filters")
    years = sorted(df.year.unique(), reverse=True)
    selected_years = st.multiselect("Year", years, years)

    df_f = df[df.year.isin(selected_years)]

# -------------------------------------------------
# VISUALS
# -------------------------------------------------
import plotly.express as px

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    fig = px.pie(
        df_f,
        names="threat_type",
        title="Threat Types",
        template=C["plotly"]
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    fig = px.bar(
        df_f.groupby("country").size().reset_index(name="count"),
        x="count",
        y="country",
        orientation="h",
        title="Top Targeted Countries",
        template=C["plotly"]
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# DATA TABLE
# -------------------------------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)

if st.session_state.view_mode == "Internal":
    st.dataframe(df_f, use_container_width=True)
else:
    st.dataframe(
        df_f.drop(columns=["actor", "source"], errors="ignore"),
        use_container_width=True
    )

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# EXPORT
# -------------------------------------------------
def export_csv():
    buf = io.StringIO()
    df_f.to_csv(buf, index=False)
    return buf.getvalue()

with st.sidebar:
    st.markdown("### Export")
    st.download_button(
        "Download CSV",
        export_csv(),
        "cyhawk_report.csv",
        "text/csv"
    )

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown(
    f"""
<p style="text-align:center;color:{C["muted"]};font-size:0.8rem;">
CyHawk Africa | Showing {len(df_f)} of {len(df)} records | Updated {datetime.now().strftime("%Y-%m-%d %H:%M")}
</p>
""",
    unsafe_allow_html=True,
)
