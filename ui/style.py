import streamlit as st

PRIMARY_COLOR = "#b30000"   # example GUC-like red
SECONDARY_COLOR = "#222222"
ACCENT_COLOR = "#ffcc00"

def setup_page():
    st.set_page_config(
        page_title="Business Simulation",
        page_icon="📊",
        layout="wide"
    )
    add_branding()

def add_branding():
    st.markdown(
        f"""
        <style>
        .main {{
            background-color: #fafafa;
        }}
        .sidebar .sidebar-content {{
            background-color: {SECONDARY_COLOR};
            color: white;
        }}
        .sidebar .sidebar-content a {{
            color: #ffffff !important;
        }}
        .css-18e3th9 {{
            padding-top: 0rem;
        }}
        .guc-header {{
            padding: 0.5rem 1rem;
            background-color: {PRIMARY_COLOR};
            color: white;
            font-weight: 600;
            border-radius: 0 0 8px 8px;
            margin-bottom: 1rem;
        }}
        </style>
        <div class="guc-header">
            Business  Simulation – GIU
        </div>
        """,
        unsafe_allow_html=True
    )
