# ==========================================================
# INTELLIGENCE LAYER – NO UI / STRUCTURE CHANGES
# ==========================================================

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from datetime import datetime
import os
import pandas as pd

# ----------------------------------------------------------
# THREAT ACTOR TYPE CLASSIFICATION
# ----------------------------------------------------------

THREAT_ACTOR_TYPES = {
    "Keymous Plus": "Hacktivist Group",
    "Anonymous Sudan": "Hacktivist Group",
    "KillSec": "Hacktivist Group",

    "Nightspire": "Ransomware Group",
    "LockBit": "Ransomware Group",
    "Akira": "Ransomware Group",
    "Qilin": "Ransomware Group",

    "b4bayega": "Data Breach / Leak Actor",
    "DatabaseHub": "Data Breach / Leak Actor",

    "BigBrother": "Initial Access Broker (IAB)",
    "Genesis Market": "Initial Access Broker (IAB)",

    "APT28": "State-Sponsored APT",
    "Lazarus Group": "State-Sponsored APT"
}

def get_actor_type(actor: str) -> str:
    return THREAT_ACTOR_TYPES.get(actor, "Unclassified Threat Actor")

# ----------------------------------------------------------
# MITRE ATT&CK – TYPE-DRIVEN MAPPING
# ----------------------------------------------------------

MITRE_ATTACK_BY_TYPE = {
    "Ransomware Group": [
        "T1566 – Phishing",
        "T1059 – Command and Scripting Interpreter",
        "T1078 – Valid Accounts",
        "T1021 – Remote Services",
        "T1486 – Data Encrypted for Impact",
        "T1041 – Exfiltration Over C2 Channel"
    ],

    "Hacktivist Group": [
        "T1499 – Endpoint Denial of Service",
        "T1498 – Network Denial of Service",
        "T1566 – Phishing",
        "T1589 – Gather Victim Identity Information",
        "T1598 – Phishing for Information"
    ],

    "Initial Access Broker (IAB)": [
        "T1078 – Valid Accounts",
        "T1133 – External Remote Services",
        "T1190 – Exploit Public-Facing Application",
        "T1110 – Brute Force",
        "T1046 – Network Service Scanning"
    ],

    "Data Breach / Leak Actor": [
        "T1041 – Exfiltration Over C2 Channel",
        "T1567 – Exfiltration Over Web Service",
        "T1537 – Transfer Data to Cloud Account",
        "T1005 – Data from Local System"
    ],

    "State-Sponsored APT": [
        "T1566 – Spearphishing",
        "T1059 – Command and Scripting Interpreter",
        "T1105 – Ingress Tool Transfer",
        "T1027 – Obfuscated Files or Information",
        "T1071 – Application Layer Protocol",
        "T1082 – System Information Discovery"
    ]
}

def resolve_mitre_ttps(actor: str) -> list:
    return MITRE_ATTACK_BY_TYPE.get(
        get_actor_type(actor),
        ["T1595 – Active Scanning"]
    )

# ----------------------------------------------------------
# EXECUTIVE SUMMARY – STRATEGIC CTI
# ----------------------------------------------------------

def generate_executive_summary(actor: str, df: pd.DataFrame) -> str:
    actor_type = get_actor_type(actor)
    actor_df = df[df["actor"] == actor]

    if actor_df.empty:
        return (
            f"{actor} is assessed as a {actor_type}. "
            "At the time of reporting, CyHawk Africa has insufficient verified telemetry "
            "to produce a statistically significant operational assessment. "
            "Continued intelligence collection is recommended."
        )

    total = len(actor_df)
    countries = actor_df["country"].nunique()
    sectors = actor_df["sector"].nunique()
    high_sev = len(actor_df[actor_df["severity"] == "High"])

    first_seen = actor_df["date"].min().strftime("%B %Y")
    last_seen = actor_df["date"].max().strftime("%B %Y")

    focus_map = {
        "Ransomware Group": "financial extortion through data encryption and data theft",
        "Hacktivist Group": "ideological or politically motivated disruption operations",
        "Initial Access Broker (IAB)": "monetization of unauthorized network access",
        "Data Breach / Leak Actor": "unauthorized data exposure and underground distribution",
        "State-Sponsored APT": "long-term espionage and strategic intelligence collection"
    }

    focus = focus_map.get(actor_type, "multi-stage intrusion activity")

    return f"""
**Executive Summary**

{actor} is assessed as a **{actor_type}** with confirmed activity observed between
**{first_seen} and {last_seen}**.

CyHawk Africa has documented **{total} incidents** attributed to this actor, impacting
**{countries} countries** and **{sectors} industry sectors**. Observed activity indicates
a primary focus on **{focus}**.

Notably, **{high_sev} high-severity incidents** were recorded, highlighting elevated
risk exposure for affected organizations.

Based on attack volume, severity distribution, and geographic spread, this threat actor
should be considered **operationally significant** within the African cyber threat landscape.
"""

# ----------------------------------------------------------
# PDF REPORT – STRATEGIC THREAT INTELLIGENCE
# ----------------------------------------------------------

def draw_branding(canvas: canvas.Canvas, doc):
    width, height = A4

    # Watermark
    canvas.saveState()
    canvas.setFont("Helvetica-Bold", 42)
    canvas.setFillColor(HexColor("#EEEEEE"))
    canvas.translate(300, 400)
    canvas.rotate(45)
    canvas.drawCentredString(0, 0, "CYHAWK AFRICA")
    canvas.restoreState()

    # Logo
    logo_path = "assets/cyhawk_logo.png"
    if os.path.exists(logo_path):
        canvas.drawImage(
            logo_path,
            40,
            height - 80,
            width=60,
            height=60,
            mask="auto"
        )

    # Footer
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(HexColor("#666666"))
    canvas.drawString(
        40,
        30,
        f"CyHawk Africa | Strategic Threat Intelligence Report | {datetime.utcnow().strftime('%d %B %Y')}"
    )

def generate_pdf_report(actor: str, df: pd.DataFrame):
    summary = generate_executive_summary(actor, df)
    mitre_ttps = resolve_mitre_ttps(actor)

    filename = f"CyHawk_{actor}_Strategic_Threat_Report.pdf"
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=100,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"<b>{actor} Threat Actor Profile</b>", styles["Title"]))
    story.append(Spacer(1, 20))

    story.append(Paragraph(summary, styles["Normal"]))
    story.append(Spacer(1, 20))

    story.append(Paragraph("<b>MITRE ATT&CK Mapping</b>", styles["Heading2"]))
    for ttp in mitre_ttps:
        story.append(Paragraph(f"- {ttp}", styles["Normal"]))

    doc.build(
        story,
        onFirstPage=draw_branding,
        onLaterPages=draw_branding
    )

    return filename
