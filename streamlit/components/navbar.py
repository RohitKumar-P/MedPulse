import streamlit as st
import config

def render_sidebar():
    with st.sidebar:
        st.markdown(
            f"""
            <div style="padding: 0.5rem 0 1.5rem 0;">
                <h3 style="margin:0; color:#0f172a; font-weight:700;">{config.APP_NAME}</h3>
                <p style="margin:0; font-size:0.8rem; color:#0284c7;">{config.TAGLINE}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        user_name = st.session_state.get("user_name", "Patient User")
        st.caption(f"Logged in as **{user_name}**")

        st.markdown("---")

        options = [
            ("Overview", "overview"),
            ("AI Screening", "screening"),
            ("Health Tracking", "tracking"),
            ("Wearables", "wearables"),
            ("Diet & Lifestyle", "diet"),
            ("Reports", "reports"),
            ("Profile", "profile"),
            ("Settings", "settings")
        ]

        current_page = st.session_state.get("current_page", "overview")
        
        for label, page_key in options:
            btn_type = "primary" if current_page == page_key else "secondary"
            if st.button(label, key=f"nav_{page_key}", use_container_width=True, type=btn_type):
                st.session_state["current_page"] = page_key
                st.rerun()

        st.markdown("---")
        
        if st.session_state.get("demo_mode", False):
            st.markdown('<span class="badge-demo">Demo Mode Active</span>', unsafe_allow_html=True)
            st.caption("Backend offline. Using fallback engine.")

        st.markdown("<br/><br/>", unsafe_allow_html=True)
        if st.button("Sign Out", key="logout_btn", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["current_page"] = "landing"
            st.rerun()

def render_public_navbar():
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; gap:10px;">
                <h3 style="margin:0; font-weight:800; color:#0f172a;">{config.APP_NAME}</h3>
                <span style="color:#64748b; font-size:0.9rem;">| {config.TAGLINE}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c2:
        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            if st.button("Sign In", key="pub_signin", use_container_width=True):
                st.session_state["current_page"] = "login"
                st.rerun()
        with btn_c2:
            if st.button("Get Started", key="pub_getstarted", type="primary", use_container_width=True):
                st.session_state["current_page"] = "signup"
                st.rerun()
