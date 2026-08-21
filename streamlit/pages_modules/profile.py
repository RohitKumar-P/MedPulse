import streamlit as st
from components.ui import render_header, render_disclaimer

def render_profile():
    render_header("Patient Profile & Clinical Baseline", subtitle="Manage baseline physical attributes and clinical history.", category="Profile")

    with st.form("profile_form"):
        st.markdown("#### Personal Information")
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Full Name", value=st.session_state.get("user_name", "Patient User"))
            st.number_input("Age", value=45, min_value=1, max_value=120)
            st.selectbox("Biological Sex", ["Male", "Female", "Other"])
        with c2:
            st.number_input("Height (cm)", value=175)
            st.number_input("Weight (kg)", value=74)
            st.text_input("Blood Type", value="A+")

        st.markdown("#### Known Medical Profile")
        st.text_area("Known Pre-existing Conditions", value="Mild Essential Hypertension")
        st.text_area("Current Medications", value="Lisinopril 10mg daily")
        st.text_area("Known Allergies", value="Penicillin")

        if st.form_submit_button("Save Profile Updates", type="primary"):
            st.success("Clinical profile updated successfully.")

    render_disclaimer()
