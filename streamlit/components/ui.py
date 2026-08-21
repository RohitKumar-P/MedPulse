import streamlit as st
import config

def render_disclaimer():
    st.markdown(
        f"""
        <div class="disclaimer-box">
            <strong>Medical Disclaimer:</strong> {config.LEGAL_DISCLAIMER}
        </div>
        """,
        unsafe_allow_html=True
    )

def render_header(title: str, subtitle: str = None, category: str = None):
    cat_html = f'<span style="color: #0284c7; font-weight: 600; font-size: 0.85rem; text-transform: uppercase;">{category}</span><br/>' if category else ''
    sub_html = f'<p style="color: #64748b; font-size: 1rem; margin-top: 0.25rem;">{subtitle}</p>' if subtitle else ''
    
    st.markdown(
        f"""
        <div style="margin-bottom: 1.5rem;">
            {cat_html}
            <h2 style="margin: 0; font-weight: 700; color: #0f172a;">{title}</h2>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True
    )

def render_risk_badge(risk_level: str) -> str:
    risk_upper = risk_level.upper()
    if risk_upper in ["LOW", "NORMAL", "HEALTHY"]:
        return '<span class="badge-low">LOW RISK</span>'
    elif risk_upper in ["MODERATE", "ELEVATED_MILD", "BORDERLINE"]:
        return '<span class="badge-moderate">MODERATE RISK</span>'
    else:
        return '<span class="badge-elevated">ELEVATED RISK</span>'
