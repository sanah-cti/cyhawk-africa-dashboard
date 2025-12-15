import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ==================================================
# PAGE CONFIG (minimal, safe)
# ==================================================
st.set_page_config(
    page_title="CyHawk Africa | CTI Dashboard",
    layout="wide"
)

# ==================================================
# HEARTBEAT – proves app execution
# ==================================================
st.write("🚀 CyHawk Africa dashboard started")

# ==================================================
# DATA LOADING WITH FULL ERROR HANDLING
# ==================================================
DATA_PATH = Path("data/incidents.csv")

st.write("📊 Initializing data load...")

def load_data_safe(path: Path) -> pd.DataFrame:
    """Safely load incident data with explicit error handling."""
    if not path.exists():
        st.error(f"❌ Data file not found: {path}")
        st.stop()

    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        st.error("❌ Data file is empty.")
        st.stop()
    except pd.errors.ParserError as e:
        st.error(f"❌ CSV parsing error: {e}")
        st.stop()
    except Exception as e:
        st.error(f"❌ Unexpected error while loading data: {e}")
        st.stop()

    if df.empty:
        st.error("❌ Data file loaded but contains no records.")
        st.stop()

    return df

df = load_data_safe(DATA_PATH)
st.success("✅ Data loaded successfully")

# ==================================================
# VALIDATE REQUIRED COLUMNS
# ==================================================
REQUIRED_COLUMNS = [
    "date",
    "actor",
    "country",
    "threat_type",
    "sector",
    "severity",
    "source",
]

missing_columns = [c for c in REQUIRED_COLUMNS if c not in df.columns]

if missing_columns:
    st.error(f"❌ Missing required columns: {missing_columns}")
    st.stop()

# ==================================================
# SAFE DATA TRANSFORMS
# ==================================================
st.write("🧹 Preparing data...")

df["date"] = pd.to_datetime(df["date"], errors="coerce")

if df["date"].isna().all():
    st.error("❌ All date values are invalid. Check date format.")
    st.stop()

df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month_name()
df["quarter"] = df["date"].dt.to_period("Q").astype(str)
df["day"] = df["date"].dt.date

st.success("✅ Data preparation complete")

# ==================================================
# SIDEBAR FILTERS (SAFE DEFAULTS)
# ==================================================
st.sidebar.markdown("## Filters")

year_filter = st.sidebar.multiselect(
    "Year",
    sorted(df["year"].dropna().unique()),
    default=sorted(df["year"].dropna().unique()),
)

severity_filter = st.sidebar.multiselect(
    "Severity",
    sorted(df["severity"].dropna().unique()),
    default=sorted(df["severity"].dropna().unique()),
)

filtered_df = df[
    df["year"].isin(year_filter)
    & df["severity"].isin(severity_filter)
]

# ==================================================
# EMPTY RESULT GUARD
# ==================================================
if filtered_df.empty:
    st.warning(
        "⚠️ No records match the selected filters. "
        "Adjust filters to view data."
    )
    st.stop()

# ==================================================
# METRICS
# ==================================================
st.divider()
st.subheader("Overview")

m1, m2, m3 = st.columns(3)

m1.metric("Total Incidents", len(filtered_df))
m2.metric("Threat Actors", filtered_df["actor"].nunique())
m3.metric("Countries Impacted", filtered_df["country"].nunique())

# ==================================================
# BASIC CHART (SAFE)
# ==================================================
st.divider()
st.subheader("Threat Type Distribution")

threat_dist = (
    filtered_df["threat_type"]
    .value_counts()
    .reset_index()
    .rename(columns={"index": "Threat Type", "threat_type": "Count"})
)

if threat_dist.empty:
    st.info("No data available for threat distribution.")
else:
    fig = px.bar(
        threat_dist,
        x="Threat Type",
        y="Count",
        title="Threat Types Observed",
    )
    st.plotly_chart(fig, use_container_width=True)

# ==================================================
# DATA TABLE
# ==================================================
st.divider()
st.subheader("Threat Intelligence Records")

st.dataframe(
    filtered_df.sort_values("date", ascending=False),
    use_container_width=True,
)

# ==================================================
# CSV EXPORT (SAFE)
# ==================================================
st.divider()
st.download_button(
    "Download Filtered Data (CSV)",
    data=filtered_df.to_csv(index=False),
    file_name="cyhawk_filtered_data.csv",
    mime="text/csv",
)

# ==================================================
# FOOTER
# ==================================================
st.caption(
    "© CyHawk Africa | Open-source African Cyber Threat Intelligence. "
    "This dashboard reflects observed activity and does not necessarily "
    "indicate the time of compromise."
)
