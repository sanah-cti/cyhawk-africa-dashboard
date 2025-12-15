import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# BASIC PAGE CONFIG (no images, no assets)
# --------------------------------------------------
st.set_page_config(
    page_title="CyHawk Africa | CTI Dashboard",
    layout="wide"
)

# --------------------------------------------------
# HEARTBEAT (confirms app execution)
# --------------------------------------------------
st.write("🚀 CyHawk Africa dashboard started")

# --------------------------------------------------
# LOAD DATA (NO CACHE, NO PARSE_DATES YET)
# --------------------------------------------------
st.write("📊 Loading data...")

try:
    df = pd.read_csv("data/incidents.csv")
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

st.success("✅ Data loaded successfully")

# --------------------------------------------------
# BASIC CLEANING (SAFE)
# --------------------------------------------------
required_columns = [
    "date", "actor", "country",
    "threat_type", "sector",
    "severity", "source"
]

missing_cols = [c for c in required_columns if c not in df.columns]
if missing_cols:
    st.error(f"Missing required columns: {missing_cols}")
    st.stop()

# Convert date AFTER load
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# Add time fields
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month_name()
df["quarter"] = df["date"].dt.to_period("Q").astype(str)
df["day"] = df["date"].dt.date

# --------------------------------------------------
# SIDEBAR FILTERS (MINIMAL)
# --------------------------------------------------
st.sidebar.markdown("## Filters")

year_filter = st.sidebar.multiselect(
    "Year",
    sorted(df["year"].dropna().unique()),
    default=sorted(df["year"].dropna().unique())
)

severity_filter = st.sidebar.multiselect(
    "Severity",
    sorted(df["severity"].dropna().unique()),
    default=sorted(df["severity"].dropna().unique())
)

filtered_df = df[
    (df["year"].isin(year_filter)) &
    (df["severity"].isin(severity_filter))
]

# --------------------------------------------------
# EMPTY GUARD
# --------------------------------------------------
if filtered_df.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# --------------------------------------------------
# METRICS (SAFE)
# --------------------------------------------------
m1, m2, m3 = st.columns(3)

m1.metric("Total Incidents", len(filtered_df))
m2.metric("Threat Actors", filtered_df["actor"].nunique())
m3.metric("Countries", filtered_df["country"].nunique())

st.divider()

# --------------------------------------------------
# SIMPLE CHART (ONLY ONE)
# --------------------------------------------------
st.subheader("Threat Type Distribution")

threat_dist = (
    filtered_df["threat_type"]
    .value_counts()
    .reset_index()
    .rename(columns={"index": "Threat Type", "threat_type": "Count"})
)

fig = px.bar(
    threat_dist,
    x="Threat Type",
    y="Count",
    title="Threat Types Observed"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# --------------------------------------------------
# DATA TABLE
# --------------------------------------------------
st.subheader("Threat Records")
st.dataframe(
    filtered_df.sort_values("date", ascending=False),
    use_container_width=True
)

st.divider()

# --------------------------------------------------
# CSV EXPORT (SAFE)
# --------------------------------------------------
st.download_button(
    "Download CSV",
    data=filtered_df.to_csv(index=False),
    file_name="cyhawk_filtered_data.csv",
    mime="text/csv"
)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.caption(
    "© CyHawk Africa | Open-source African Cyber Threat Intelligence. "
    "This dashboard reflects observed activity and does not necessarily "
    "indicate the time of compromise."
)


