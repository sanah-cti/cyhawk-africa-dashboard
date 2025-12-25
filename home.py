import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
import random

# ═══════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="CyHawk Africa - Threat Intelligence Platform",
    page_icon="assets/favicon.ico",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════
# THEME MANAGEMENT
# ═══════════════════════════════════════════════════════════
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

THEMES = {
    'dark': {
        'bg': '#000000',
        'bg_elevated': '#0a0a0a',
        'bg_card': '#111111',
        'border': '#1f1f1f',
        'text': '#ffffff',
        'text_dim': '#999999',
        'text_subtle': '#666666',
        'cyhawk_red': '#C41E3A',
        'red_glow': 'rgba(196, 30, 58, 0.5)',
        'success': '#00ff00',
    },
    'light': {
        'bg': '#ffffff',
        'bg_elevated': '#f8f9fa',
        'bg_card': '#f0f0f0',
        'border': '#e0e0e0',
        'text': '#000000',
        'text_dim': '#666666',
        'text_subtle': '#999999',
        'cyhawk_red': '#C41E3A',
        'red_glow': 'rgba(196, 30, 58, 0.3)',
        'success': '#27ae60',
    }
}

C = THEMES[st.session_state.theme]

# ═══════════════════════════════════════════════════════════
# COUNTRY TO ISO MAPPING
# ═══════════════════════════════════════════════════════════
COUNTRY_ISO = {
    'Nigeria': 'NGA', 'South Africa': 'ZAF', 'Kenya': 'KEN', 'Egypt': 'EGY',
    'Ghana': 'GHA', 'Ethiopia': 'ETH', 'Tanzania': 'TZA', 'Uganda': 'UGA',
    'Morocco': 'MAR', 'Algeria': 'DZA', 'Sudan': 'SDN', 'Angola': 'AGO',
    'Mozambique': 'MOZ', 'Madagascar': 'MDG', 'Cameroon': 'CMR', 'Ivory Coast': 'CIV',
    'Niger': 'NER', 'Mali': 'MLI', 'Burkina Faso': 'BFA', 'Malawi': 'MWI',
    'Zambia': 'ZMB', 'Senegal': 'SEN', 'Somalia': 'SOM', 'Chad': 'TCD',
    'Zimbabwe': 'ZWE', 'Guinea': 'GIN', 'Rwanda': 'RWA', 'Benin': 'BEN',
    'Tunisia': 'TUN', 'Burundi': 'BDI', 'South Sudan': 'SSD', 'Togo': 'TGO',
    'Sierra Leone': 'SLE', 'Libya': 'LBY', 'Liberia': 'LBR', 'Mauritania': 'MRT',
    'Central African Republic': 'CAF', 'Eritrea': 'ERI', 'Gambia': 'GMB',
    'Botswana': 'BWA', 'Namibia': 'NAM', 'Gabon': 'GAB', 'Lesotho': 'LSO',
    'Guinea-Bissau': 'GNB', 'Equatorial Guinea': 'GNQ', 'Mauritius': 'MUS',
    'Eswatini': 'SWZ', 'Djibouti': 'DJI', 'Comoros': 'COM',
    'Cape Verde': 'CPV', 'Sao Tome and Principe': 'STP', 'Seychelles': 'SYC'
}

# ═══════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def load_data():
    """Load incidents data from CSV - REQUIRED"""
    
    # Try to find CSV file
    csv_paths = ['data/incidents.csv', '../data/incidents.csv', 'incidents.csv']
    csv_path = None
    
    for path in csv_paths:
        if os.path.exists(path):
            csv_path = path
            break
    
    if not csv_path:
        st.error("⚠️ **ERROR: incidents.csv file not found!**")
        st.info("""
        **Required CSV file location:** `data/incidents.csv`
        
        **Required columns:**
        - `date` - Date of incident (YYYY-MM-DD format)
        - `actor` - Name of threat actor/group
        - `country` - African country name
        - `threat_type` - Type of threat (Database, DDoS, etc.)
        - `sector` - Target industry/sector
        - `severity` - Severity level (Critical, High, Medium, Low)
        - `source` - Source of information
        
        **Example CSV format:**
        ```
        date,actor,country,threat_type,sector,severity,source
        2025-09-03,ifalcon,Sudan,Database,Telecommunications,Medium,Dark Web
        2025-09-03,Keymous Plus,Morocco,DDoS,Government,Medium,Telegram
        ```
        
        Please add the incidents.csv file to the `data/` directory and refresh the page.
        """)
        st.stop()
    
    try:
        # Load CSV
        df = pd.read_csv(csv_path)
        
        # Map your column names to our expected names
        column_mapping = {
            'actor': 'threat_actor',
            'threat_type': 'threat_type',
            'sector': 'industry',
            'severity': 'severity',
            'country': 'country',
            'date': 'date',
            'source': 'source'
        }
        
        # Check which columns exist and map them
        existing_mapping = {}
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                existing_mapping[old_name] = new_name
        
        # Rename columns
        df = df.rename(columns=existing_mapping)
        
        # Validate required columns (after mapping)
        required_columns = ['date', 'country', 'threat_actor', 'threat_type', 'severity']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"⚠️ **ERROR: Missing required columns in CSV file!**")
            st.info(f"""
            **Missing columns:** {', '.join(missing_columns)}
            
            **Required columns (your CSV format):**
            - `date` - Date of incident (YYYY-MM-DD format)
            - `actor` - Name of threat actor/group
            - `country` - African country name
            - `threat_type` - Type of threat (Database, DDoS, etc.)
            - `sector` - Target industry/sector
            - `severity` - Severity level (Critical, High, Medium, Low)
            - `source` - Source of information (optional)
            
            **Your CSV has these columns:** {', '.join(df.columns.tolist())}
            
            Please update your CSV file with all required columns.
            """)
            st.stop()
        
        # Process date column
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Check for invalid dates
        invalid_dates = df['date'].isna().sum()
        if invalid_dates > 0:
            st.warning(f"⚠️ Warning: {invalid_dates} rows have invalid dates and will be removed.")
        
        df = df.dropna(subset=['date'])
        
        if len(df) == 0:
            st.error("⚠️ **ERROR: No valid data in CSV file after processing!**")
            st.info("Please check that your CSV file contains valid dates in YYYY-MM-DD format.")
            st.stop()
        
        # Add derived columns
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.strftime('%B')
        
        # Add industry column if missing (it's mapped from 'sector')
        if 'industry' not in df.columns:
            df['industry'] = 'Unknown'
        
        # Clean up data - remove rows with missing critical data
        initial_count = len(df)
        df = df.dropna(subset=['country', 'threat_actor', 'threat_type', 'severity'])
        removed_count = initial_count - len(df)
        
        if removed_count > 0:
            st.warning(f"⚠️ Warning: Removed {removed_count} rows with missing data.")
        
        if len(df) == 0:
            st.error("⚠️ **ERROR: No valid data remaining after cleanup!**")
            st.stop()
        
        # Success message
        st.success(f"✅ Successfully loaded {len(df)} incidents from {csv_path}")
        
        return df
        
    except Exception as e:
        st.error(f"⚠️ **ERROR loading CSV file:** {str(e)}")
        st.info("""
        Please check that:
        1. The CSV file is properly formatted
        2. All required columns are present: date, actor, country, threat_type, sector, severity
        3. The file is not corrupted
        4. Dates are in YYYY-MM-DD format
        """)
        st.stop()

def filter_data(df, year, month, country, threat_type, threat_actor, severity):
    """Apply all filters"""
    filtered = df.copy()
    
    if year != "All Years":
        filtered = filtered[filtered['year'] == int(year)]
    if month != "All Months":
        filtered = filtered[filtered['month'] == month]
    if country != "All Countries":
        filtered = filtered[filtered['country'] == country]
    if threat_type != "All Types":
        filtered = filtered[filtered['threat_type'] == threat_type]
    if threat_actor != "All Actors":
        filtered = filtered[filtered['threat_actor'] == threat_actor]
    if severity != "All Severities":
        filtered = filtered[filtered['severity'] == severity]
    
    return filtered

def process_map_data(df):
    """Process data for map"""
    map_data = []
    
    for country, iso in COUNTRY_ISO.items():
        country_df = df[df['country'] == country]
        attacks = len(country_df)
        
        top_actors = []
        if not country_df.empty:
            for actor, count in country_df['threat_actor'].value_counts().head(5).items():
                top_actors.append({'name': str(actor), 'count': int(count)})
        
        threat_types = []
        if not country_df.empty:
            for ttype, count in country_df['threat_type'].value_counts().head(3).items():
                threat_types.append({'type': str(ttype), 'count': int(count)})
        
        map_data.append({
            'country': country,
            'iso_alpha': iso,
            'attacks': attacks,
            'top_actors': top_actors,
            'threat_types': threat_types
        })
    
    return pd.DataFrame(map_data)


# ═══════════════════════════════════════════════════════════
# PDF EXPORT - COMPREHENSIVE STRATEGIC THREAT INTELLIGENCE REPORT
# ═══════════════════════════════════════════════════════════
def add_watermark(canvas, doc):
    """Add CyHawk Africa watermark and logo to every page"""
    canvas.saveState()
    
    # Large diagonal watermark
    canvas.setFont('Helvetica-Bold', 60)
    canvas.setFillColorRGB(0.85, 0.85, 0.85, alpha=0.15)
    canvas.translate(A4[0]/2, A4[1]/2)
    canvas.rotate(45)
    canvas.drawCentredString(0, 0, "CYHAWK AFRICA")
    canvas.rotate(-45)
    canvas.translate(-A4[0]/2, -A4[1]/2)
    
    # Try to add logo to header (only if not first page)
    page_num = canvas.getPageNumber()
    if page_num > 1:
        try:
            logo_path = "assets/cyhawk_logo.png"
            if os.path.exists(logo_path):
                canvas.drawImage(logo_path, 40, A4[1] - 50, width=30, height=30, preserveAspectRatio=True, mask='auto')
        except:
            pass  # Logo not found, continue without it
    
    # Footer with page number
    canvas.restoreState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColorRGB(0.5, 0.5, 0.5)
    
    # Page number
    text = f"Page {page_num}"
    canvas.drawRightString(A4[0] - 30, 20, text)
    
    # CyHawk footer branding
    canvas.setFillColorRGB(0.77, 0.12, 0.23)  # CyHawk Red
    canvas.setFont('Helvetica-Bold', 8)
    canvas.drawString(30, 20, "CyHawk Africa | Threat Intelligence Platform")
    
    # TLP:WHITE classification banner at top
    canvas.setFillColorRGB(1, 1, 1)  # White background
    canvas.rect(A4[0]/2 - 60, A4[1] - 25, 120, 15, fill=1, stroke=1)
    canvas.setStrokeColorRGB(0.8, 0.8, 0.8)
    canvas.setFillColorRGB(0, 0, 0)  # Black text
    canvas.setFont('Helvetica-Bold', 9)
    canvas.drawCentredString(A4[0]/2, A4[1] - 17, "TLP:WHITE")

def generate_pdf(df, filters):
    """Generate comprehensive strategic threat intelligence report"""
    buffer = io.BytesIO()
    
    # Create document with custom page template
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=60,
        bottomMargin=40
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#C41E3A'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=34
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=16,
        textColor=colors.HexColor('#333333'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#C41E3A'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold',
        borderWidth=0,
        borderColor=colors.HexColor('#C41E3A'),
        borderPadding=5,
        leftIndent=0
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12,
        leading=14,
        alignment=TA_LEFT
    )
    
    # ==================== COVER PAGE ====================
    elements.append(Spacer(1, 40))
    
    # Add logo at top if available
    try:
        logo_path = "assets/cyhawk_logo.png"
        if os.path.exists(logo_path):
            logo = RLImage(logo_path, width=80, height=80)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 20))
    except:
        pass  # Logo not found, continue without it
    
    # Title with logo placeholder
    elements.append(Paragraph("CyHawk Africa", title_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("STRATEGIC THREAT INTELLIGENCE REPORT", subtitle_style))
    
    elements.append(Spacer(1, 40))
    
    # Report metadata box
    report_date = datetime.now().strftime('%B %d, %Y')
    report_period = f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}"
    
    meta_data = [
        ['Report Date:', report_date],
        ['Reporting Period:', report_period],
        ['Classification:', 'TLP:WHITE'],
        ['Distribution:', 'Unlimited Distribution Permitted'],
        ['Total Incidents:', str(len(df))],
        ['Geographic Scope:', f"{df['country'].nunique()} African Countries"]
    ]
    
    meta_table = Table(meta_data, colWidths=[2.5*inch, 3*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F0F0')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#C41E3A')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#FAFAFA')]),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(meta_table)
    elements.append(Spacer(1, 60))
    
    # Applied filters
    active_filters = {k: v for k, v in filters.items() if not str(v).startswith('All')}
    if active_filters:
        elements.append(Paragraph("ACTIVE FILTERS", heading_style))
        filter_text = "<br/>".join([f"<b>{k}:</b> {v}" for k, v in active_filters.items()])
        elements.append(Paragraph(filter_text, body_style))
        elements.append(Spacer(1, 20))
    
    # Disclaimer
    disclaimer_style = ParagraphStyle('Disclaimer', parent=styles['Normal'], fontSize=8, 
                                     textColor=colors.grey, alignment=TA_CENTER, leading=10)
    disclaimer = """TLP:WHITE - This information may be distributed without restriction, subject to 
    copyright controls. Recipients may share TLP:WHITE information freely without constraints."""
    elements.append(Spacer(1, 100))
    elements.append(Paragraph(disclaimer, disclaimer_style))
    
    # Page break
    elements.append(Spacer(1, 0.1*inch))
    elements.append(PageBreak())
    
    # ==================== EXECUTIVE SUMMARY ====================
    elements.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
    
    # Calculate key metrics
    total_incidents = len(df)
    critical_count = len(df[df['severity'] == 'Critical'])
    high_count = len(df[df['severity'] == 'High'])
    countries_affected = df['country'].nunique()
    threat_actors = df['threat_actor'].nunique()
    most_targeted = df['country'].value_counts().head(3)
    top_actor = df['threat_actor'].value_counts().iloc[0]
    top_threat_type = df['threat_type'].value_counts().iloc[0]
    
    summary_text = f"""
    This strategic threat intelligence report provides a comprehensive analysis of cyber threats 
    targeting African organizations during the reporting period. The analysis is based on 
    <b>{total_incidents}</b> confirmed security incidents across <b>{countries_affected}</b> African nations.<br/><br/>
    
    <b>KEY FINDINGS:</b><br/>
    • <b>{critical_count}</b> incidents classified as CRITICAL severity, requiring immediate action<br/>
    • <b>{high_count}</b> incidents classified as HIGH severity<br/>
    • <b>{threat_actors}</b> distinct threat actor groups identified<br/>
    • <b>{top_threat_type}</b> emerged as the primary attack vector with <b>{df['threat_type'].value_counts().iloc[0]}</b> incidents<br/>
    • <b>{top_actor}</b> identified as the most active threat actor<br/><br/>
    
    <b>GEOGRAPHIC IMPACT:</b><br/>
    The most heavily targeted nations include {', '.join([f"{country} ({count} incidents)" for country, count in most_targeted.items()])}. 
    This geographic distribution suggests a coordinated targeting of key economic and governmental infrastructure 
    across the continent.
    """
    
    elements.append(Paragraph(summary_text, body_style))
    elements.append(Spacer(1, 20))
    
    # ==================== THREAT LANDSCAPE OVERVIEW ====================
    elements.append(Paragraph("THREAT LANDSCAPE OVERVIEW", heading_style))
    
    summary_data = [
        ['METRIC', 'VALUE', 'SEVERITY ASSESSMENT'],
        ['Total Incidents', str(total_incidents), 'MONITORING'],
        ['Critical Severity', str(critical_count), 'IMMEDIATE ACTION REQUIRED'],
        ['High Severity', str(high_count), 'PRIORITY RESPONSE'],
        ['Medium Severity', str(len(df[df['severity'] == 'Medium'])), 'STANDARD MONITORING'],
        ['Low Severity', str(len(df[df['severity'] == 'Low'])), 'ROUTINE OBSERVATION'],
        ['Unique Threat Actors', str(threat_actors), 'TRACKING ACTIVE'],
        ['Countries Affected', str(countries_affected), 'CONTINENTAL SCOPE'],
    ]
    
    summary_table = Table(summary_data, colWidths=[2.2*inch, 1.3*inch, 2.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C41E3A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9F9F9')]),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    # ==================== THREAT TYPE DISTRIBUTION ====================
    elements.append(PageBreak())
    elements.append(Paragraph("THREAT TYPE DISTRIBUTION", heading_style))
    
    threat_counts = df['threat_type'].value_counts()
    threat_data = [['THREAT TYPE', 'INCIDENTS', 'PERCENTAGE', 'TREND']]
    
    for threat, count in threat_counts.head(10).items():
        percentage = f"{(count/len(df)*100):.1f}%"
        trend = "↑ INCREASING" if percentage else "→ STABLE"
        threat_data.append([threat, str(count), percentage, trend])
    
    threat_table = Table(threat_data, colWidths=[2*inch, 1.2*inch, 1.3*inch, 1.5*inch])
    threat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C41E3A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9F9F9')]),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(threat_table)
    elements.append(Spacer(1, 20))
    
    # ==================== THREAT ACTOR ANALYSIS ====================
    elements.append(Paragraph("THREAT ACTOR INTELLIGENCE", heading_style))
    
    actor_counts = df['threat_actor'].value_counts()
    actor_data = [['THREAT ACTOR', 'INCIDENTS', 'PERCENTAGE', 'THREAT LEVEL']]
    
    for actor, count in actor_counts.head(15).items():
        percentage = f"{(count/len(df)*100):.1f}%"
        if float(percentage.rstrip('%')) > 10:
            level = "CRITICAL"
        elif float(percentage.rstrip('%')) > 5:
            level = "HIGH"
        else:
            level = "MEDIUM"
        actor_data.append([actor, str(count), percentage, level])
    
    actor_table = Table(actor_data, colWidths=[2.2*inch, 1*inch, 1.2*inch, 1.6*inch])
    actor_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C41E3A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9F9F9')]),
        ('FONTNAME', (3, 1), (3, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (3, 1), (3, -1), colors.HexColor('#C41E3A')),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(actor_table)
    elements.append(Spacer(1, 20))
    
    # ==================== GEOGRAPHIC ANALYSIS ====================
    elements.append(PageBreak())
    elements.append(Paragraph("GEOGRAPHIC THREAT DISTRIBUTION", heading_style))
    
    country_counts = df['country'].value_counts()
    geo_data = [['COUNTRY', 'INCIDENTS', 'PERCENTAGE', 'RISK LEVEL']]
    
    for country, count in country_counts.head(20).items():
        percentage = f"{(count/len(df)*100):.1f}%"
        if count > total_incidents * 0.1:
            risk = "CRITICAL"
        elif count > total_incidents * 0.05:
            risk = "HIGH"
        elif count > total_incidents * 0.02:
            risk = "MEDIUM"
        else:
            risk = "LOW"
        geo_data.append([country, str(count), percentage, risk])
    
    geo_table = Table(geo_data, colWidths=[2.2*inch, 1*inch, 1.2*inch, 1.6*inch])
    geo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C41E3A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9F9F9')]),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(geo_table)
    elements.append(Spacer(1, 20))
    
    # ==================== INDUSTRY TARGETING ====================
    if 'industry' in df.columns:
        elements.append(Paragraph("INDUSTRY SECTOR ANALYSIS", heading_style))
        
        industry_counts = df['industry'].value_counts()
        industry_data = [['INDUSTRY SECTOR', 'INCIDENTS', 'PERCENTAGE', 'PRIORITY']]
        
        for industry, count in industry_counts.head(10).items():
            percentage = f"{(count/len(df)*100):.1f}%"
            priority = "CRITICAL" if count > total_incidents * 0.15 else "HIGH" if count > total_incidents * 0.1 else "MEDIUM"
            industry_data.append([industry, str(count), percentage, priority])
        
        industry_table = Table(industry_data, colWidths=[2.2*inch, 1*inch, 1.2*inch, 1.6*inch])
        industry_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C41E3A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9F9F9')]),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(industry_table)
        elements.append(Spacer(1, 20))
    
    # ==================== RECOMMENDATIONS ====================
    elements.append(PageBreak())
    elements.append(Paragraph("STRATEGIC RECOMMENDATIONS", heading_style))
    
    recommendations = f"""
    Based on the analysis of <b>{total_incidents}</b> security incidents, CyHawk Africa recommends 
    the following strategic actions:<br/><br/>
    
    <b>1. IMMEDIATE ACTIONS (CRITICAL PRIORITY)</b><br/>
    • Deploy enhanced monitoring for the {critical_count} critical-severity incidents<br/>
    • Implement emergency response protocols for high-risk countries: {', '.join(most_targeted.head(3).index)}<br/>
    • Activate threat hunting operations targeting {top_actor} infrastructure<br/><br/>
    
    <b>2. SHORT-TERM INITIATIVES (30-60 DAYS)</b><br/>
    • Strengthen defenses against {top_threat_type} attack vectors<br/>
    • Conduct security assessments of critical infrastructure in high-risk nations<br/>
    • Enhance information sharing partnerships with regional CERTs<br/>
    • Deploy advanced detection signatures for identified threat actors<br/><br/>
    
    <b>3. LONG-TERM STRATEGIC INITIATIVES (90+ DAYS)</b><br/>
    • Establish continental threat intelligence sharing framework<br/>
    • Develop sector-specific security baselines for critical industries<br/>
    • Implement proactive threat hunting programs<br/>
    • Build regional incident response capabilities<br/><br/>
    
    <b>4. INTELLIGENCE GAPS</b><br/>
    • Limited visibility in {54 - countries_affected} African nations<br/>
    • Need for enhanced private sector threat data sharing<br/>
    • Requirement for attribution capabilities improvement<br/>
    """
    
    elements.append(Paragraph(recommendations, body_style))
    elements.append(Spacer(1, 30))
    
    # ==================== FINAL PAGE ====================
    elements.append(PageBreak())
    elements.append(Spacer(1, 100))
    
    elements.append(Paragraph("ABOUT CYHAWK AFRICA", heading_style))
    about_text = """
    CyHawk Africa is the continent's leading threat intelligence platform, providing real-time 
    cyber threat monitoring and analysis across 54 African countries. Our mission is to protect 
    African digital infrastructure through advanced threat detection, intelligence sharing, and 
    strategic security advisories.<br/><br/>
    
    <b>FOR MORE INFORMATION:</b><br/>
    Website: dashboard.cyhawk-africa.com<br/>
    Email: intel@cyhawk-africa.com<br/><br/>
    
    <b>TRAFFIC LIGHT PROTOCOL:</b><br/>
    <b>Classification:</b> TLP:WHITE<br/>
    <b>Distribution:</b> Unlimited - May be shared freely<br/>
    <b>Audience:</b> Public information suitable for public disclosure<br/>
    <b>Retention:</b> No restrictions<br/><br/>
    
    <b>TLP:WHITE</b> information may be distributed without restriction, subject to standard 
    copyright rules. Recipients may share TLP:WHITE information freely.
    """
    elements.append(Paragraph(about_text, body_style))
    
    # Build PDF with watermark
    doc.build(elements, onFirstPage=add_watermark, onLaterPages=add_watermark)
    
    buffer.seek(0)
    return buffer

# Load data
df = load_data()

# ═══════════════════════════════════════════════════════════
# CSS STYLING
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {{ font-family: 'Inter', sans-serif; -webkit-font-smoothing: antialiased; }}
.stApp {{ background: {C['bg']}; color: {C['text']}; }}
#MainMenu, footer, header {{ visibility: hidden; }}

/* Remove default Streamlit padding */
.main .block-container {{
    padding-top: 0 !important;
    max-width: 100% !important;
}}

.stApp::before {{
    content: ''; position: fixed; inset: 0;
    background-image: 
        linear-gradient({C['red_glow']} 1px, transparent 1px),
        linear-gradient(90deg, {C['red_glow']} 1px, transparent 1px);
    background-size: 50px 50px; z-index: -1; opacity: 0.3;
}}

.main-header {{
    background: rgba(10, 10, 10, 0.95); backdrop-filter: blur(20px);
    border-bottom: 1px solid {C['border']}; padding: 1.5rem 3rem;
    display: flex; justify-content: space-between; align-items: center;
    margin: 0 0 2rem 0;
    position: sticky;
    top: 0;
    z-index: 1000;
    width: 100%;
}}

.logo-section {{ display: flex; align-items: center; gap: 1rem; }}
.logo-container {{
    width: 50px; height: 50px; background: {C['cyhawk_red']};
    border-radius: 50%; box-shadow: 0 0 20px {C['red_glow']};
    flex-shrink: 0;
}}

.brand-text h1 {{ font-size: 1.5rem; font-weight: 600; margin: 0; }}
.brand-highlight {{ color: {C['cyhawk_red']}; font-weight: 700; }}
.brand-text p {{
    font-size: 0.75rem; color: {C['text_dim']};
    text-transform: uppercase; letter-spacing: 2px; margin: 0;
}}

.header-nav {{
    display: flex; gap: 2rem; align-items: center;
}}

.nav-link {{
    color: {C['text_dim']}; text-decoration: none;
    font-size: 0.9rem; font-weight: 500;
    transition: color 0.2s;
}}

.nav-link:hover {{ color: {C['text']}; }}
.nav-link.active {{ color: {C['cyhawk_red']}; }}

.status-indicator {{
    display: flex; align-items: center; gap: 0.5rem;
    padding: 0.5rem 1rem; background: rgba(0, 255, 0, 0.1);
    border: 1px solid {C['success']}; border-radius: 20px;
}}

.status-dot {{
    width: 8px; height: 8px; background: {C['success']};
    border-radius: 50%; animation: pulse 2s infinite;
}}

@keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} }}

.hero-label {{
    color: {C['cyhawk_red']}; font-size: 0.75rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 2px; margin-bottom: 1rem;
    margin-top: 2rem;
}}
.hero-label::before {{
    content: ''; display: inline-block; width: 30px; height: 2px;
    background: {C['cyhawk_red']}; margin-right: 0.5rem;
}}

.hero-title {{
    font-size: 3.5rem; font-weight: 700; margin-bottom: 1rem;
    letter-spacing: -2px; line-height: 1.1;
}}

.hero-subtitle {{ font-size: 1.25rem; color: {C['text_dim']}; margin-bottom: 2rem; }}

.map-container {{
    background: linear-gradient(135deg, {C['bg_card']} 0%, {C['bg_elevated']} 100%);
    border: 1px solid {C['border']}; border-radius: 24px;
    padding: 3rem; margin-bottom: 2rem; position: relative; overflow: hidden;
}}

.stats-grid {{
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 1.5rem; margin: 2rem 0;
}}

.stat-card {{
    background: {C['bg_card']}; border: 1px solid {C['border']};
    border-radius: 16px; padding: 1.5rem; transition: all 0.3s;
}}

.stat-card:hover {{ border-color: {C['cyhawk_red']}; transform: translateY(-4px); }}

.stat-value {{
    font-size: 2.5rem; font-weight: 700; color: {C['cyhawk_red']};
    line-height: 1; margin-bottom: 0.25rem;
}}

.stat-label {{
    font-size: 0.85rem; color: {C['text_dim']};
    text-transform: uppercase; letter-spacing: 1px;
}}

.legend {{
    display: flex; gap: 2rem; padding: 1.5rem 0;
    border-top: 1px solid {C['border']}; flex-wrap: wrap;
}}

.legend-item {{ display: flex; align-items: center; gap: 0.75rem; }}
.legend-dot {{ width: 12px; height: 12px; border-radius: 50%; }}

.section-header {{ margin: 3rem 0 2rem 0; }}
.section-label {{
    color: {C['cyhawk_red']}; font-size: 0.7rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 2px; margin-bottom: 0.75rem;
}}
.section-title {{ font-size: 2rem; font-weight: 700; }}

.chart-card {{
    background: {C['bg_card']}; border: 1px solid {C['border']};
    border-radius: 20px; padding: 2rem; margin-bottom: 2rem;
    transition: all 0.3s;
}}

.chart-card:hover {{ border-color: rgba(196, 30, 58, 0.5); }}

.chart-header {{
    display: flex; justify-content: space-between;
    align-items: center; margin-bottom: 1.5rem;
}}

.chart-title {{ font-size: 1.1rem; font-weight: 600; }}

.chart-badge {{
    background: rgba(196, 30, 58, 0.1); color: {C['cyhawk_red']};
    padding: 0.4rem 0.9rem; border-radius: 20px;
    font-size: 0.7rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1px;
}}

.filter-container {{
    background: {C['bg_card']}; border: 1px solid {C['border']};
    border-radius: 16px; padding: 1.5rem; margin-bottom: 2rem;
}}

.stSelectbox label {{
    font-size: 0.75rem !important; color: {C['text_subtle']} !important;
    text-transform: uppercase; letter-spacing: 1px; font-weight: 600 !important;
}}

.stButton > button {{
    background: {C['cyhawk_red']} !important; color: white !important;
    border: none !important; border-radius: 12px !important;
    padding: 0.75rem 1.5rem !important; font-weight: 600 !important;
}}

.block-container {{ 
    padding-top: 0 !important;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1400px;
    margin: 0 auto;
}}

@media (max-width: 1024px) {{
    .main-header {{
        padding: 1rem 1.5rem;
        flex-wrap: wrap;
        gap: 1rem;
    }}
    
    .header-nav {{
        width: 100%;
        justify-content: space-between;
    }}
}}

@media (max-width: 768px) {{
    .stats-grid {{ grid-template-columns: 1fr; }}
    .hero-title {{ font-size: 2rem; }}
    
    .main-header {{
        padding: 1rem;
    }}
    
    .header-nav {{
        gap: 1rem;
        flex-wrap: wrap;
    }}
    
    .nav-link {{
        font-size: 0.8rem;
    }}
}}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
<div class="main-header">
    <div class="logo-section">
        <div class="logo-container"></div>
        <div class="brand-text">
            <h1><span class="brand-highlight">CyHawk</span> Africa</h1>
            <p>Threat Intelligence Platform</p>
        </div>
    </div>
    <div class="header-nav">
        <a href="/" target="_self" class="nav-link active">Home</a>
        <a href="/Threat_Actors" target="_self" class="nav-link">Threat Actors</a>
        <a href="/Actor_Profile" target="_self" class="nav-link">Actor Profile</a>
        <a href="/Trending_Attacks" target="_self" class="nav-link">Trending Attacks</a>
        <div class="status-indicator">
            <div class="status-dot"></div>
            <span style="color: {C['text_dim']}; font-size: 0.85rem;">Live</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    if st.button("🌓 Toggle Theme", use_container_width=True):
        toggle_theme()
        st.rerun()

# ═══════════════════════════════════════════════════════════
# HERO
# ═══════════════════════════════════════════════════════════
st.markdown('<div style="max-width: 1400px; margin: 0 auto; padding: 0 2rem;">', unsafe_allow_html=True)

st.markdown(f"""
<div class="hero-label">CONTINENTAL INTELLIGENCE</div>
<h1 class="hero-title">Africa Threat Landscape</h1>
<p class="hero-subtitle">Real-time cyber threat monitoring across African nations</p>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# FILTERS
# ═══════════════════════════════════════════════════════════
st.markdown('<div class="filter-container">', unsafe_allow_html=True)

c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    years = ["All Years"] + sorted([str(y) for y in df['year'].unique()], reverse=True)
    year = st.selectbox("Year", years)

with c2:
    months = ["All Months", "January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    month = st.selectbox("Month", months)

with c3:
    countries = ["All Countries"] + sorted(df['country'].unique().tolist())
    country = st.selectbox("Country", countries)

with c4:
    types = ["All Types"] + sorted(df['threat_type'].unique().tolist())
    threat_type = st.selectbox("Threat Type", types)

with c5:
    actors = ["All Actors"] + sorted(df['threat_actor'].unique().tolist())
    actor = st.selectbox("Threat Actor", actors)

with c6:
    sevs = ["All Severities", "Critical", "High", "Medium", "Low"]
    severity = st.selectbox("Severity", sevs)

st.markdown('</div>', unsafe_allow_html=True)

filtered_df = filter_data(df, year, month, country, threat_type, actor, severity)

# ═══════════════════════════════════════════════════════════
# AFRICA MAP
# ═══════════════════════════════════════════════════════════
map_df = process_map_data(filtered_df)

st.markdown('<div class="map-container">', unsafe_allow_html=True)

hover_texts = []
for _, row in map_df.iterrows():
    actors_txt = ""
    if row['top_actors']:
        actors_txt = "<br><b>Top Actors:</b>"
        for a in row['top_actors'][:5]:
            actors_txt += f"<br>  • {a['name']}: {a['count']}"
    
    types_txt = ""
    if row['threat_types']:
        types_txt = "<br><b>Top Threats:</b>"
        for t in row['threat_types'][:3]:
            types_txt += f"<br>  • {t['type']}: {t['count']}"
    
    hover_texts.append(f"<b>{row['country']}</b><br>Attacks: {row['attacks']}{actors_txt}{types_txt}")

fig = go.Figure(go.Choropleth(
    locations=map_df['iso_alpha'], z=map_df['attacks'], locationmode='ISO-3',
    colorscale=[[0, '#0D47A1'], [0.4, '#00E676'], [0.5, '#FFEB3B'], [0.7, '#FF9800'], [1, '#C41E3A']],
    marker=dict(line=dict(color=C['border'], width=0.5)),
    colorbar=dict(title="Threats", titlefont=dict(color=C['text']), tickfont=dict(color=C['text'])),
    text=hover_texts, hovertemplate='%{text}<extra></extra>'
))

fig.update_geos(
    scope='africa', projection_type='natural earth',
    showland=True, landcolor=C['bg_elevated'],
    showocean=True, oceancolor=C['bg'],
    showcountries=True, countrycolor=C['border'], bgcolor=C['bg_card']
)

fig.update_layout(
    height=650, margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor='rgba(0,0,0,0)', geo=dict(bgcolor='rgba(0,0,0,0)'),
    font=dict(color=C['text'])
)

st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# STATS
# ═══════════════════════════════════════════════════════════
total = len(filtered_df)
crit_high = len(filtered_df[filtered_df['severity'].isin(['Critical', 'High'])])
actors_cnt = filtered_df['threat_actor'].nunique()
countries_cnt = filtered_df['country'].nunique()

st.markdown(f"""
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-value">{total}</div>
        <div class="stat-label">Total Threats</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">{crit_high}</div>
        <div class="stat-label">Critical & High</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">{actors_cnt}</div>
        <div class="stat-label">Threat Actors</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">{countries_cnt}</div>
        <div class="stat-label">Countries</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="legend">
    <div class="legend-item"><div class="legend-dot" style="background: #0D47A1;"></div><span>Safe</span></div>
    <div class="legend-item"><div class="legend-dot" style="background: #00E676;"></div><span>Low</span></div>
    <div class="legend-item"><div class="legend-dot" style="background: #FFEB3B;"></div><span>Moderate</span></div>
    <div class="legend-item"><div class="legend-dot" style="background: #FF9800;"></div><span>High</span></div>
    <div class="legend-item"><div class="legend-dot" style="background: #C41E3A;"></div><span>Critical</span></div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# ANALYTICS SECTION 1: TOP RANSOMWARE & THREATS
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
<div class="section-header">
    <div class="section-label">ANALYSIS</div>
    <h2 class="section-title">Threat Intelligence</h2>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="chart-header">
        <h3 class="chart-title">Top Ransomware Groups</h3>
        <span class="chart-badge">Ransomware Activity</span>
    </div>
    """, unsafe_allow_html=True)
    
    ransomware_df = filtered_df[filtered_df['threat_type'] == 'Ransomware']
    ransomware_actors = ransomware_df['threat_actor'].value_counts().head(10)
    
    fig1 = go.Figure(go.Bar(
        y=ransomware_actors.index,
        x=ransomware_actors.values,
        orientation='h',
        marker=dict(color='#C41E3A'),
        hovertemplate='<b>%{y}</b><br>Count: %{x}<extra></extra>'
    ))
    
    fig1.update_layout(
        height=300, margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor=C['border'], showgrid=True, color=C['text']),
        yaxis=dict(gridcolor=C['border'], showgrid=False, color=C['text']),
        font=dict(color=C['text'])
    )
    
    st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="chart-header">
        <h3 class="chart-title">Top Threats</h3>
        <span class="chart-badge">Threat Type Breakdown</span>
    </div>
    """, unsafe_allow_html=True)
    
    threat_counts = filtered_df['threat_type'].value_counts().head(10)
    
    colors_map = {'Ransomware': '#C41E3A', 'Phishing': '#FF9800', 'DDoS': '#FFEB3B', 
                  'Malware': '#00E676', 'Data Breach': '#00BCD4'}
    bar_colors = [colors_map.get(t, '#999999') for t in threat_counts.index]
    
    fig2 = go.Figure(go.Bar(
        x=threat_counts.index,
        y=threat_counts.values,
        marker=dict(color=bar_colors),
        hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
    ))
    
    fig2.update_layout(
        height=300, margin=dict(l=20, r=20, t=20, b=40),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor=C['border'], showgrid=False, color=C['text'], tickangle=-45),
        yaxis=dict(gridcolor=C['border'], showgrid=True, color=C['text']),
        font=dict(color=C['text'])
    )
    
    st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# ANALYTICS SECTION 2: CLASSIFICATION & SEVERITY
# ═══════════════════════════════════════════════════════════
col3, col4 = st.columns(2)

with col3:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="chart-header">
        <h3 class="chart-title">Threat Classification</h3>
        <span class="chart-badge">By Type</span>
    </div>
    """, unsafe_allow_html=True)
    
    class_counts = filtered_df['threat_type'].value_counts()
    
    fig3 = go.Figure(go.Bar(
        y=class_counts.index,
        x=class_counts.values,
        orientation='h',
        marker=dict(color='#C41E3A'),
        hovertemplate='<b>%{y}</b><br>Count: %{x}<extra></extra>'
    ))
    
    fig3.update_layout(
        height=300, margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor=C['border'], showgrid=True, color=C['text']),
        yaxis=dict(gridcolor=C['border'], showgrid=False, color=C['text']),
        font=dict(color=C['text'])
    )
    
    st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="chart-header">
        <h3 class="chart-title">Severity Analysis</h3>
        <span class="chart-badge">Impact Level</span>
    </div>
    """, unsafe_allow_html=True)
    
    sev_counts = filtered_df['severity'].value_counts()
    sev_colors = {'Critical': '#9C27B0', 'Medium': '#FFA726', 'High': '#C41E3A', 'Low': '#66BB6A', 'Unknown': '#757575'}
    sev_bar_colors = [sev_colors.get(s, '#999999') for s in sev_counts.index]
    
    fig4 = go.Figure(go.Bar(
        x=sev_counts.index,
        y=sev_counts.values,
        marker=dict(color=sev_bar_colors),
        hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
    ))
    
    fig4.update_layout(
        height=300, margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor=C['border'], showgrid=False, color=C['text']),
        yaxis=dict(gridcolor=C['border'], showgrid=True, color=C['text']),
        font=dict(color=C['text'])
    )
    
    st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# ANALYTICS SECTION 3: TIMELINE
# ═══════════════════════════════════════════════════════════
st.markdown('<div class="chart-card">', unsafe_allow_html=True)
st.markdown(f"""
<div class="chart-header">
    <h3 class="chart-title">Activity Timeline</h3>
    <span class="chart-badge">Historical Trend</span>
</div>
""", unsafe_allow_html=True)

timeline_df = filtered_df.groupby(filtered_df['date'].dt.to_period('D')).size().reset_index(name='count')
timeline_df['date'] = timeline_df['date'].dt.to_timestamp()

fig5 = go.Figure(go.Scatter(
    x=timeline_df['date'],
    y=timeline_df['count'],
    mode='lines',
    line=dict(color='#C41E3A', width=2),
    fill='tozeroy',
    fillcolor='rgba(196, 30, 58, 0.1)',
    hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Count: %{y}<extra></extra>'
))

fig5.update_layout(
    height=250, margin=dict(l=20, r=20, t=20, b=20),
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(gridcolor=C['border'], showgrid=True, color=C['text']),
    yaxis=dict(gridcolor=C['border'], showgrid=True, color=C['text']),
    font=dict(color=C['text'])
)

st.plotly_chart(fig5, use_container_width=True, config={'displayModeBar': False})
st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# ANALYTICS SECTION 4: ACTORS & INDUSTRIES
# ═══════════════════════════════════════════════════════════
col5, col6 = st.columns(2)

with col5:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="chart-header">
        <h3 class="chart-title">Top Threat Actors</h3>
        <span class="chart-badge">Most Active</span>
    </div>
    """, unsafe_allow_html=True)
    
    top_actors = filtered_df['threat_actor'].value_counts().head(10)
    
    fig6 = go.Figure(go.Bar(
        y=top_actors.index,
        x=top_actors.values,
        orientation='h',
        marker=dict(color='#C41E3A'),
        hovertemplate='<b>%{y}</b><br>Count: %{x}<extra></extra>'
    ))
    
    fig6.update_layout(
        height=300, margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor=C['border'], showgrid=True, color=C['text']),
        yaxis=dict(gridcolor=C['border'], showgrid=False, color=C['text']),
        font=dict(color=C['text'])
    )
    
    st.plotly_chart(fig6, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with col6:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="chart-header">
        <h3 class="chart-title">Most Targeted Industries</h3>
        <span class="chart-badge">Sector Analysis</span>
    </div>
    """, unsafe_allow_html=True)
    
    industries = filtered_df['industry'].value_counts().head(10)
    
    fig7 = go.Figure(go.Bar(
        y=industries.index,
        x=industries.values,
        orientation='h',
        marker=dict(color='#C41E3A'),
        hovertemplate='<b>%{y}</b><br>Count: %{x}<extra></extra>'
    ))
    
    fig7.update_layout(
        height=300, margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor=C['border'], showgrid=True, color=C['text']),
        yaxis=dict(gridcolor=C['border'], showgrid=False, color=C['text']),
        font=dict(color=C['text'])
    )
    
    st.plotly_chart(fig7, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# PDF EXPORT
# ═══════════════════════════════════════════════════════════
st.markdown("---")
c_a, c_b = st.columns([3, 1])
with c_b:
    if st.button("Export PDF Report", type="primary", use_container_width=True):
        filters_applied = {
            'Year': year, 'Month': month, 'Country': country,
            'Type': threat_type, 'Actor': actor, 'Severity': severity
        }
        pdf_buf = generate_pdf(filtered_df, filters_applied)
        st.download_button(
            "Download PDF",
            data=pdf_buf,
            file_name=f"cyhawk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

# Close content wrapper
st.markdown('</div>', unsafe_allow_html=True)
