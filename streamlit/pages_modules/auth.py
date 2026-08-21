import streamlit as st
import config
from components.ui import render_disclaimer

def render_login():
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown(
            f"""
            <div style="text-align: center; margin-bottom: 2rem;">
                <h2 style="margin: 0; font-weight: 800;">Welcome to {config.APP_NAME}</h2>
                <p style="color: #64748b;">Sign in to access your preventive health dashboard</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form("login_form"):
            email = st.text_input("Email Address", value="demo@aegishealth.ai")
            password = st.text_input("Password", type="password", value="password123")
            remember = st.checkbox("Remember this device")
            
            submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

            if submitted:
                if email and password:
                    st.session_state["authenticated"] = True
                    st.session_state["user_email"] = email
                    st.session_state["user_name"] = email.split("@")[0].capitalize()
                    st.session_state["current_page"] = "overview"
                    st.success("Authenticated successfully.")
                    st.rerun()
                else:
                    st.error("Please enter both email and password.")

        st.caption("UI Demo Account: Enter any credentials to sign in.")
        st.markdown("---")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Create Account", key="goto_signup", use_container_width=True):
                st.session_state["current_page"] = "signup"
                st.rerun()
        with col_b:
            if st.button("Back to Home", key="login_back_home", use_container_width=True):
                st.session_state["current_page"] = "landing"
                st.rerun()

def render_signup():
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown(
            f"""
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <h2 style="margin: 0; font-weight: 800;">Create Your Account</h2>
                <p style="color: #64748b;">Join {config.APP_NAME} for intelligent risk screening</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form("signup_form"):
            f_name = st.text_input("First Name")
            l_name = st.text_input("Last Name")
            email = st.text_input("Email Address")
            p1 = st.text_input("Password", type="password")
            p2 = st.text_input("Confirm Password", type="password")
            
            st.date_input("Date of Birth")
            st.selectbox("Gender", ["Select...", "Male", "Female", "Other", "Prefer not to say"])
            
            terms = st.checkbox("I agree to the platform terms and health-data disclaimer.")
            
            submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")

            if submitted:
                if not (f_name and email and p1):
                    st.error("Please fill in all required fields.")
                elif p1 != p2:
                    st.error("Passwords do not match.")
                elif not terms:
                    st.error("You must accept the terms and medical disclaimer.")
                else:
                    st.session_state["authenticated"] = True
                    st.session_state["user_email"] = email
                    st.session_state["user_name"] = f_name
                    st.session_state["current_page"] = "overview"
                    st.success("Account created successfully.")
                    st.rerun()

        if st.button("Already have an account? Sign In", key="goto_login", use_container_width=True):
            st.session_state["current_page"] = "login"
            st.rerun()

    render_disclaimer()
