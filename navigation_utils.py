"""
Navigation and Branding Utilities for CyHawk Africa Dashboard
Add this file to your repository root
"""

import streamlit as st

def add_logo_and_branding():
    """Add clickable logo and custom branding to the sidebar"""
    st.markdown(
        """
        <style>
        /* Hide default Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Custom logo styling */
        [data-testid="stSidebar"] {
            background-color: #0D1117;
        }
        
        /* Logo container */
        .logo-container {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 1.5rem 1rem;
            margin-bottom: 2rem;
            border-bottom: 2px solid #30363D;
        }
        
        .logo-link {
            text-decoration: none;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.5rem;
            transition: transform 0.3s ease;
        }
        
        .logo-link:hover {
            transform: scale(1.05);
        }
        
        .logo-text {
            font-size: 1.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #C41E3A 0%, #9A1529 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -0.5px;
        }
        
        .logo-subtitle {
            font-size: 0.7rem;
            color: #8B949E;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Rename "app" to "Home" */
        [data-testid="stSidebarNav"] li:first-child a span {
            display: none;
        }
        
        [data-testid="stSidebarNav"] li:first-child a::after {
            content: "Home";
            font-weight: 600;
        }
        
        /* Navigation styling */
        [data-testid="stSidebarNav"] {
            padding-top: 0;
        }
        
        [data-testid="stSidebarNav"] a {
            background-color: transparent;
            border-radius: 8px;
            padding: 0.75rem 1rem;
            margin: 0.25rem 0;
            transition: all 0.3s ease;
        }
        
        [data-testid="stSidebarNav"] a:hover {
            background-color: #1C2128;
            border-left: 3px solid #C41E3A;
        }
        
        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background-color: #1C2128;
            border-left: 3px solid #C41E3A;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Add clickable logo to sidebar
    with st.sidebar:
        st.markdown(
            """
            <div class="logo-container">
                <a href="https://cyhawk-africa.com" target="_blank" class="logo-link">
                    <div class="logo-text">CYHAWK AFRICA</div>
                    <div class="logo-subtitle">Threat Intelligence</div>
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )

def set_page_config(page_title="CyHawk Africa Dashboard", page_icon="🔒", layout="wide"):
    """Set consistent page configuration across all pages"""
    st.set_page_config(
        page_title=page_title,
        page_icon=page_icon,
        layout=layout,
        initial_sidebar_state="expanded",
        menu_items={
            'Report a cyber incident': 'https://cyhawk-africa.com/contact',
            'Report a bug': 'https://cyhawk-africa.com/contact',
            'Support Us': 'https://buymeacoffee.com/cyhawk',
            'About': 'CyHawk Africa - Cyber Threat Intelligence Platform'
          
        }
    )
