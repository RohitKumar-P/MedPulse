import streamlit as st
import config
from components.ui import render_header, render_risk_badge, render_disclaimer

def render_results():
    render_header("Screening Assessment Result", subtitle="Evaluated risk metrics and AI model prediction outputs.", category="Results")

    result = st.session_state.get("latest_result")
    if not result:
        st.error("No active screening result found. Please execute a screening first.")
        if st.button("Go to Screening"):
            st.session_state["current_page"] = "screening"
            st.rerun()
        return

    risk_level = result.get("risk_level", "MODERATE")
    risk_score = result.get("risk_score", 0.0)
    disease_name = result.get("disease", "Target Screening")

    st.markdown(
        f"""
        <div class="aegis-card" style="text-align: center; padding: 2.5rem 1.5rem;">
            <span style="color: #64748b; font-size: 0.9rem; font-weight: 600;">ASSESSMENT TARGET</span>
            <h2 style="margin: 0.2rem 0 1rem 0;">{disease_name}</h2>
            <div>{render_risk_badge(risk_level)}</div>
            <h1 style="font-size: 3.5rem; font-weight: 800; margin: 1rem 0 0 0; color: #0f172a;">{risk_score}%</h1>
            <p style="color: #64748b; margin: 0;">Calculated Risk Probability Index</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Clinical Interpretation")
    if risk_level.upper() == "LOW":
        st.success("The provided biomarkers align with a low probabilistic risk profile for this category. Continue routine health maintenance.")
    elif risk_level.upper() == "MODERATE":
        st.warning("Biomarkers indicate moderate risk indicators. Lifestyle modifications and routine clinical consultation are recommended.")
    else:
        st.error("Elevated risk indicators detected based on submitted clinical metrics. Consult a healthcare provider for formal diagnostic testing.")

    r_c1, r_c2, r_c3 = st.columns(3)
    with r_c1:
        if st.button("View Preventive Recommendations", type="primary", use_container_width=True):
            st.session_state["current_page"] = "diet"
            st.rerun()
    with r_c2:
        if st.button("Download Summary Report (PDF)", use_container_width=True):
            st.info("Report generation queued (Placeholder).")
    with r_c3:
        if st.button("New Screening Assessment", use_container_width=True):
            st.session_state["current_page"] = "screening"
            st.rerun()

    render_disclaimer()
