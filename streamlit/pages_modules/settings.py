import streamlit as st
import config
from components.ui import render_header

def render_settings():
    render_header("Platform Settings", subtitle="Configure API connection endpoints and data preferences.", category="Settings")

    st.markdown("#### Backend Service Configuration")
    api_url = st.text_input("FastAPI Backend Base URL", value=config.API_BASE_URL)
    
    if st.button("Test Connection"):
        from services.api_client import AegisAPIClient
        client = AegisAPIClient(base_url=api_url)
        if client.check_health():
            st.success(f"Successfully connected to Aegis Backend at {api_url}")
        else:
            st.error(f"Failed to connect to backend at {api_url}. Operating in Demo Mode.")

    st.markdown("---")
    st.markdown("#### Data Management")
    st.button("Clear Local Session Data", type="secondary")
    st.button("Delete Account Data", type="primary", disabled=True)
    st.caption("Account deletion requires connected backend auth microservice.")
