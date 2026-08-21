import streamlit as st
import pandas as pd
from components.ui import render_header, render_risk_badge, render_disclaimer

def render_dashboard():
    user_name = st.session_state.get("user_name", "Patient")
    render_header(f"Welcome back, {user_name}", subtitle="Here is your latest health-risk overview and recent screenings.", category="Dashboard")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            """
            <div class="aegis-card">
                <span style="color:#64748b; font-size:0.8rem; font-weight:600;">ACTIVE SCREENINGS</span>
                <h3 style="margin:0.2rem 0; font-weight:700;">3 Models</h3>
                <span style="color:#166534; font-size:0.75rem;">Completed this month</span>
            </div>
            """, unsafe_allow_html=True
        )
    with m2:
        st.markdown(
            """
            <div class="aegis-card">
                <span style="color:#64748b; font-size:0.8rem; font-weight:600;">PRIMARY RISK STATUS</span>
                <h3 style="margin:0.2rem 0; font-weight:700;">Low Risk</h3>
                <span style="color:#64748b; font-size:0.75rem;">Cardiovascular primary</span>
            </div>
            """, unsafe_allow_html=True
        )
    with m3:
        st.markdown(
            """
            <div class="aegis-card">
                <span style="color:#64748b; font-size:0.8rem; font-weight:600;">HEALTH SCORE</span>
                <h3 style="margin:0.2rem 0; font-weight:700;">N/A</h3>
                <span style="color:#64748b; font-size:0.75rem;">Complete full assessment</span>
            </div>
            """, unsafe_allow_html=True
        )
    with m4:
        st.markdown(
            """
            <div class="aegis-card">
                <span style="color:#64748b; font-size:0.8rem; font-weight:600;">WEARABLE SYNC</span>
                <h3 style="margin:0.2rem 0; font-weight:700; color:#94a3b8;">Offline</h3>
                <span style="color:#0284c7; font-size:0.75rem;">Integration pending</span>
            </div>
            """, unsafe_allow_html=True
        )

    st.markdown("<br/>", unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("### Recent AI Screening Activity")
        history = st.session_state.get("screening_history", [])
        
        if not history:
            st.info("No recent screening assessments found. Start your first AI screening below.")
        else:
            df = pd.DataFrame(history)
            st.dataframe(df, use_container_width=True)

        if st.button("Run New AI Screening", type="primary"):
            st.session_state["current_page"] = "screening"
            st.rerun()

    with c2:
        st.markdown("### Next Steps")
        st.markdown(
            """
            <div class="aegis-card">
                <strong>1. Complete Baseline Screening</strong>
                <p style="font-size:0.85rem; color:#64748b;">Execute Cardiovascular and Diabetes screening models.</p>
                <strong>2. Update Clinical Profile</strong>
                <p style="font-size:0.85rem; color:#64748b;">Ensure blood pressure and lab values are current.</p>
                <strong>3. Review Guidance</strong>
                <p style="font-size:0.85rem; color:#64748b;">Check personalized preventive recommendations.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    render_disclaimer()
