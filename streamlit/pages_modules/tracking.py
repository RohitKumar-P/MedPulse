import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from components.ui import render_header, render_disclaimer

def render_tracking():
    render_header("Health Tracking & Vitals", subtitle="Longitudinal logging of physiological metrics over time.", category="Analytics")

    st.caption("Data Mode: Demonstration Dataset (Labeled for testing)")

    dates = pd.date_range(end=pd.Timestamp.now(), periods=30, freq='D')
    np.random.seed(42)
    
    sys_bp = np.random.normal(122, 5, 30)
    dia_bp = np.random.normal(78, 4, 30)
    hr = np.random.normal(72, 6, 30)
    
    df = pd.DataFrame({
        "Date": dates,
        "Systolic BP": sys_bp,
        "Diastolic BP": dia_bp,
        "Heart Rate": hr
    })

    t1, t2 = st.tabs(["Blood Pressure Trend", "Heart Rate Log"])

    with t1:
        fig_bp = px.line(df, x="Date", y=["Systolic BP", "Diastolic BP"], 
                         title="30-Day Blood Pressure Progression (mmHg)",
                         color_discrete_sequence=["#ef4444", "#3b82f6"])
        fig_bp.update_layout(template="plotly_white", yaxis_range=[60, 160])
        st.plotly_chart(fig_bp, use_container_width=True)

    with t2:
        fig_hr = px.line(df, x="Date", y="Heart Rate", 
                         title="Resting Heart Rate (BPM)",
                         color_discrete_sequence=["#10b981"])
        fig_hr.update_layout(template="plotly_white", yaxis_range=[50, 100])
        st.plotly_chart(fig_hr, use_container_width=True)

    render_disclaimer()
