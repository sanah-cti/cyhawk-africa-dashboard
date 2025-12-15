import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="CyHawk Africa | Threat Intelligence Platform",
    page_icon="assets/cyhawk_logo.png",
    layout="wide"
)

# --------------------------------------------------
# Header
# --------------------------------------------------
col_logo, col_title = st.columns([1, 7])

with col_logo:
    st.image("assets/cyhawk_logo.png", width=90)

with col_title:
    st.title("CyHawk Africa – Cyber Threat Intelligence Platform")
    st.caption(
        "Africa-focused cyber threat intelligence derived from open-source reporting. "
        "Severity reflects analyst assessment and may evolve as investigations continue."
    )

st.divider()

# --------------------------------------------------
# Load data
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/incidents.csv", parse_dates=["date"])
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month_name()
    df["quarter"] = df["date"].dt.to_period("Q").astype(str)
    df["day"] = df["date"].dt.date
    return df

df = load_data()

# --------------------------------------------------
# Sidebar filters
# --------------------------------------------------
st.sidebar.image("assets/cyhawk_logo.png", width=130)
st.sidebar.markdown("## Filters")

year_filter = st.sidebar.multiselect(
    "Year",
    sorted(df["year"].unique()),
    default=sorted(df["year"].unique())
)

month_filter = st.sidebar.multiselect(
    "Month",
    df["month"].unique(),
    default=df["month"].unique()
)

quarter_filter = st.sidebar.multiselect(
    "Quarter",
    sorted(df["quarter"].unique()),
    default=sorted(df["quarter"].unique())
)

date_range = st.sidebar.date_input(
    "Date Range",
    [df["date"].min(), df["date"].max()]
)

threat_type_filter = st.sidebar.multiselect(
    "Threat Type",
    df["threat_type"].unique(),
    default=df["threat_type"].unique()
)

sector_filter = st.sidebar.multiselect(
    "Sector",
    df["sector"].unique(),
    default=df["sector"].unique()
)

actor_filter = st.sidebar.multiselect(
    "Threat Actor",
    df["actor"].unique(),
    default=df["actor"].unique()
)

severity_filter = st.sidebar.multiselect(
    "Severity",
    df["severity"].unique(),
    default=df["severity"].unique()
)

# --------------------------------------------------
# Apply filters
# --------------------------------------------------
filtered_df = df[
    (df["year"].isin(year_filter)) &
    (df["month"].isin(month_filter)) &
    (df["quarter"].isin(quarter_filter)) &
    (df["threat_type"].isin(threat_type_filter)) &
    (df["sector"].isin(sector_filter)) &
    (df["actor"].isin(actor_filter)) &
    (df["severity"].isin(severity_filter)) &
    (df["date"].dt.date >= date_range[0]) &
    (df["date"].dt.date <= date_range[1])
]

# --------------------------------------------------
# Empty dataset guard
# --------------------------------------------------
if filtered_df.empty:
    st.warning(
        "No threat intelligence records match the selected filters. "
        "Adjust filters or date range to view results."
    )
    st.stop()

# --------------------------------------------------
# Metrics
# --------------------------------------------------
m1, m2, m3, m4 = st.columns(4)

m1.metric("Total Incidents", len(filtered_df))
m2.metric("Active Threat Actors", filtered_df["actor"].nunique())
m3.metric("High Severity Incidents", len(filtered_df[filtered_df["severity"] == "High"]))
m4.metric("Countries Impacted", filtered_df["country"].nunique())

st.divider()

# --------------------------------------------------
# Charts
# --------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    threat_dist = (
        filtered_df["threat_type"]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "Threat Type", "threat_type": "Count"})
    )

    fig_threat = px.pie(
        threat_dist,
        names="Threat Type",
        values="Count",
        hole=0.45,
        title="Threat Type Distribution"
    )
    st.plotly_chart(fig_threat, use_container_width=True)

with c2:
    severity_dist = (
        filtered_df["severity"]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "Severity", "severity": "Count"})
    )

    fig_severity = px.bar(
        severity_dist,
        x="Severity",
        y="Count",
        title="Severity Breakdown"
    )
    st.plotly_chart(fig_severity, use_container_width=True)

st.divider()

# --------------------------------------------------
# Time-based analytics
# --------------------------------------------------
st.subheader("Threat Activity Over Time")

daily_df = (
    filtered_df
    .groupby("day")
    .size()
    .reset_index(name="Incidents")
)

fig_daily = px.line(
    daily_df,
    x="day",
    y="Incidents",
    title="Daily Threat Activity"
)
st.plotly_chart(fig_daily, use_container_width=True)

quarterly_df = (
    filtered_df
    .groupby("quarter")
    .size()
    .reset_index(name="Incidents")
)

fig_quarter = px.bar(
    quarterly_df,
    x="quarter",
    y="Incidents",
    title="Quarterly Threat Activity"
)
st.plotly_chart(fig_quarter, use_container_width=True)

st.divider()

# --------------------------------------------------
# Data table
# --------------------------------------------------
st.subheader("Threat Intelligence Records")
st.dataframe(
    filtered_df.sort_values("date", ascending=False),
    use_container_width=True
)

# --------------------------------------------------
# REPORT GENERATION (CSV – SAFE)
# --------------------------------------------------
st.divider()
st.header("Generate Intelligence Report")

st.download_button(
    label="Download Filtered Data (CSV)",
    data=filtered_df.to_csv(index=False),
    file_name=f"cyhawk_threat_report_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)

# --------------------------------------------------
# OPTIONAL: SAFE PDF GENERATION (ON-DEMAND)
# --------------------------------------------------
with st.expander("Generate PDF Report (Optional)"):
    st.info("PDF generation is performed on-demand and may take a few seconds.")

    if st.button("Generate PDF"):
        # Lazy import to avoid startup blocking
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet

        filename = f"CyHawk_Threat_Report_{datetime.now().strftime('%Y%m%d')}.pdf"
        doc = SimpleDocTemplate(filename)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("CyHawk Africa – Threat Intelligence Report", styles["Title"]))
        story.append(Paragraph(f"Total Incidents: {len(filtered_df)}", styles["Normal"]))
        story.append(Paragraph(f"Countries Impacted: {filtered_df['country'].nunique()}", styles["Normal"]))
        story.append(Paragraph(f"Active Threat Actors: {filtered_df['actor'].nunique()}", styles["Normal"]))

        doc.build(story)

        with open(filename, "rb") as f:
            st.download_button(
                "Download PDF Report",
                f,
                file_name=filename,
                mime="application/pdf"
            )

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.caption(
    "© CyHawk Africa | African Cyber Threat Intelligence Platform. "
    "This dashboard reflects observed activity and does not necessarily "
    "indicate the time of compromise."
)

