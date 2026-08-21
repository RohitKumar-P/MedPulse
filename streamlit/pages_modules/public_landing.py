import streamlit as st
import config
from components.navbar import render_public_navbar
from components.ui import render_disclaimer
from components.flowchart import render_aegis_flowchart

def render_landing_page():
    render_public_navbar()
    st.markdown("<br/>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="aegis-hero-card">
            <div style="max-width: 650px;">
                <span style="background: rgba(2, 132, 199, 0.2); color: #38bdf8; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">AI-POWERED PREVENTIVE HEALTHCARE</span>
                <h1 style="font-size: 2.75rem; font-weight: 800; margin: 1rem 0; line-height: 1.15;">Smarter Health Decisions Start Earlier.</h1>
                <p style="font-size: 1.1rem; color: #cbd5e1; margin-bottom: 2rem; line-height: 1.6;">
                    Aegis Health AI leverages validated machine learning models to analyze clinical vitals, biomarkers, and health indicators -- empowering individuals and clinicians with early health-risk screening estimates.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    h_btn1, h_btn2, _ = st.columns([1.5, 1.5, 3])
    with h_btn1:
        if st.button("Start Free Screening", key="hero_start", type="primary", use_container_width=True):
            st.session_state["current_page"] = "signup"
            st.rerun()
    with h_btn2:
        if st.button("Explore Platform", key="hero_explore", use_container_width=True):
            st.session_state["current_page"] = "login"
            st.rerun()

    st.markdown("<br/><br/>", unsafe_allow_html=True)

    st.markdown("### Core Capabilities")
    v1, v2, v3, v4 = st.columns(4)
    with v1:
        st.markdown(
            """
            <div class="aegis-card">
                <h4 style="margin:0 0 0.5rem 0;">AI Screening</h4>
                <p style="font-size:0.85rem; color:#64748b; margin:0;">Targeted machine learning evaluations across 10 specialized health risk categories.</p>
            </div>
            """, unsafe_allow_html=True
        )
    with v2:
        st.markdown(
            """
            <div class="aegis-card">
                <h4 style="margin:0 0 0.5rem 0;">Health Tracking</h4>
                <p style="font-size:0.85rem; color:#64748b; margin:0;">Longitudinal logging of blood pressure, blood glucose, sleep quality, and vitals.</p>
            </div>
            """, unsafe_allow_html=True
        )
    with v3:
        st.markdown(
            """
            <div class="aegis-card">
                <h4 style="margin:0 0 0.5rem 0;">Risk Analytics</h4>
                <p style="font-size:0.85rem; color:#64748b; margin:0;">Probabilistic health stratification based on objective clinical metrics.</p>
            </div>
            """, unsafe_allow_html=True
        )
    with v4:
        st.markdown(
            """
            <div class="aegis-card">
                <h4 style="margin:0 0 0.5rem 0;">Preventive Guidance</h4>
                <p style="font-size:0.85rem; color:#64748b; margin:0;">Actionable lifestyle and nutritional guidance tailored to risk findings.</p>
            </div>
            """, unsafe_allow_html=True
        )

    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("### How It Works")
    st.caption("End-to-end data processing workflow for risk estimation")
    render_aegis_flowchart()

    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("### Supported Screening Categories")
    
    models_list = list(config.DISEASE_MODELS.values())
    cols = st.columns(2)
    for idx, model in enumerate(models_list):
        with cols[idx % 2]:
            st.markdown(
                f"""
                <div class="aegis-card" style="padding:1rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <strong>{model['name']}</strong>
                        <span style="font-size:0.75rem; background:#f1f5f9; padding:2px 8px; border-radius:4px; color:#475569;">{model['category']}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("### Your Health, Beyond the Clinic")
    w1, w2 = st.columns([2, 1])
    with w1:
        st.write("Aegis Health AI is designed to aggregate multi-device health data continuously. Future integrations will ingest continuous telemetry from consumer smartwatches and clinical wearables to identify physiological changes prior to routine doctor visits.")
        st.caption("Planned Metrics: Heart Rate Variability (HRV), Resting Heart Rate, SpO2, Sleep Stages, Activity & Stress Indicators.")
    with w2:
        st.info("Wearable Data Hub Architecture (Coming Soon)")

    render_disclaimer()
