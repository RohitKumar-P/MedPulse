import streamlit as st
import pandas as pd
from components.ui import render_header, render_disclaimer

def render_reports():
    render_header("Screening Reports & History", subtitle="Review past AI screening assessments and export medical summaries.", category="Reports")

    history = st.session_state.get("screening_history", [])

    if not history:
        st.info("No completed screening reports available in this session.")
    else:
        df = pd.DataFrame(history)
        st.dataframe(df, use_container_width=True)

        st.markdown("<br/>", unsafe_allow_html=True)
        r1, r2 = st.columns(2)
        with r1:
            st.button("Download Selected Report (PDF)", key="rep_pdf", use_container_width=True)
        with r2:
            st.button("Export All Data (JSON)", key="rep_json", use_container_width=True)

    render_disclaimer()
