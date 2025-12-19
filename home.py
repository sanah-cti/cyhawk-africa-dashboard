# =============================================================================
# EXACT FIXES FOR HOME.PY
# Copy and paste these sections into your Home.py file
# =============================================================================

# -----------------------------------------------------------------------------
# FIX 1: Navigation - Change "home" to "Home" (Line ~30)
# -----------------------------------------------------------------------------
# FIND:
#     st.page_link("Home.py", label="home", icon="🏠")
# 
# REPLACE WITH:
st.page_link("Home.py", label="Home", icon="🏠")


# -----------------------------------------------------------------------------
# FIX 2: Threat Classification - Remove DDoS Duplication (Line ~200)
# -----------------------------------------------------------------------------
# FIND the threat classification section and REPLACE with this:

# Threat classification chart with case-insensitive grouping
threat_counts = df['threat_type'].str.lower().str.strip().value_counts().reset_index()
threat_counts.columns = ['Threat Type', 'Count']

# Standardize threat type names to avoid duplicates
def standardize_threat_name(name):
    """Standardize threat names to avoid case-sensitive duplicates"""
    name = str(name).strip().lower()
    
    # Map variations to standard names
    if 'ddos' in name or 'dos attack' in name or 'denial of service' in name:
        return 'DDoS'
    elif 'database' in name or 'breach' in name or 'leak' in name or 'data theft' in name:
        return 'Database'
    elif 'ransomware' in name or 'ransom' in name:
        return 'Ransomware'
    elif 'credential' in name:
        return 'Credential'
    elif 'source code' in name:
        return 'Source Code'
    elif 'access' in name and 'initial' not in name:
        return 'Access'
    elif 'vulnerability' in name or 'exploit' in name:
        return 'Vulnerability'
    elif 'defacement' in name or 'deface' in name:
        return 'Defacement'
    elif 'unknown' in name:
        return 'Unknown'
    else:
        return name.title()

threat_counts['Threat Type'] = threat_counts['Threat Type'].apply(standardize_threat_name)

# Group by standardized names and sum counts (eliminates duplicates)
threat_counts = threat_counts.groupby('Threat Type', as_index=False)['Count'].sum()

# Sort by count descending
threat_counts = threat_counts.sort_values('Count', ascending=True)

fig_threats = px.bar(threat_counts, 
                     y='Threat Type', 
                     x='Count',
                     orientation='h',
                     title='Threat Classification Distribution',
                     color='Count',
                     color_continuous_scale=['#C41E3A', '#8B1538'])

fig_threats.update_layout(
    height=400,
    showlegend=False,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(size=12),
    title_font=dict(size=16),
    xaxis=dict(
        title='Count',
        gridcolor='rgba(128,128,128,0.2)'
    ),
    yaxis=dict(
        title='Threat Type',
        gridcolor='rgba(128,128,128,0.2)'
    )
)

st.plotly_chart(fig_threats, use_container_width=True)


# -----------------------------------------------------------------------------
# FIX 3: Light Mode Legibility - Apply to ALL Charts
# -----------------------------------------------------------------------------
# After EVERY chart's fig.update_layout(), ensure these settings are included:

# For fig_severity (Severity Analysis chart):
fig_severity.update_layout(
    height=400,
    showlegend=False,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(size=12),
    title_font=dict(size=16),
    xaxis=dict(gridcolor='rgba(128,128,128,0.2)'),
    yaxis=dict(gridcolor='rgba(128,128,128,0.2)')
)

# For fig_timeline (Attack Trend Timeline):
fig_timeline.update_layout(
    height=400,
    showlegend=False,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(size=12),
    title_font=dict(size=16),
    xaxis=dict(
        title='Date',
        gridcolor='rgba(128,128,128,0.2)'
    ),
    yaxis=dict(
        title='Number of Attacks',
        gridcolor='rgba(128,128,128,0.2)'
    ),
    hovermode='x unified'
)

# For fig_geo (Geographic Distribution):
fig_geo.update_layout(
    height=500,
    showlegend=True,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(size=12),
    title_font=dict(size=16),
    geo=dict(
        bgcolor='rgba(0,0,0,0)',
        showframe=False,
        coastlinecolor='rgba(128,128,128,0.3)',
        projection_type='natural earth'
    )
)

# For any sector charts:
fig_sector.update_layout(
    height=400,
    showlegend=True,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(size=12),
    title_font=dict(size=16)
)


# -----------------------------------------------------------------------------
# SUMMARY OF CHANGES
# -----------------------------------------------------------------------------
"""
1. Navigation: "home" → "Home" ✅
2. DDoS Duplication: Fixed by case-insensitive grouping ✅
3. Light Mode Text: Made legible with proper color settings ✅

All changes preserve the existing page structure.
"""
