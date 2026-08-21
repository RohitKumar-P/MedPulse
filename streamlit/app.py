import streamlit as st
import os

st.set_page_config(
    page_title="Aegis Health AI - Preventive Health Platform",
    page_icon="???",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "custom.css")
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "landing"
if "screening_history" not in st.session_state:
    st.session_state["screening_history"] = []
if "demo_mode" not in st.session_state:
    st.session_state["demo_mode"] = False

from pages_modules.public_landing import render_landing_page
from pages_modules.auth import render_login, render_signup
from pages_modules.dashboard import render_dashboard
from pages_modules.screening import render_screening
from pages_modules.results import render_results
from pages_modules.tracking import render_tracking
from pages_modules.wearables import render_wearables
from pages_modules.diet_lifestyle import render_diet
from pages_modules.reports import render_reports
from pages_modules.profile import render_profile
from pages_modules.settings import render_settings
from components.navbar import render_sidebar

def main():
    authenticated = st.session_state["authenticated"]
    current_page = st.session_state["current_page"]

    if not authenticated:
        if current_page == "login":
            render_login()
        elif current_page == "signup":
            render_signup()
        else:
            render_landing_page()
    else:
        render_sidebar()
        
        page_map = {
            "overview": render_dashboard,
            "screening": render_screening,
            "results": render_results,
            "tracking": render_tracking,
            "wearables": render_wearables,
            "diet": render_diet,
            "reports": render_reports,
            "profile": render_profile,
            "settings": render_settings
        }

        render_fn = page_map.get(current_page, render_dashboard)
        render_fn()

if __name__ == "__main__":
    main()
