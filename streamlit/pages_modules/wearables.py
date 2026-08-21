import streamlit as st
from components.ui import render_header, render_disclaimer

def render_wearables():
    render_header("Connect Your Wearable", subtitle="Stream continuous biometric telemetry into Aegis AI engine.", category="Integrations")

    st.markdown("### Integration Status")
    
    devices = [
        ("Apple Health / Watch", "Planned Integration", "Heart Rate, HRV, SpO2, Sleep Stages"),
        ("Google Health Connect", "Planned Integration", "Steps, Active Calories, Sleep"),
        ("Fitbit OS", "Coming Soon", "Resting Heart Rate, Daily Activity"),
        ("Garmin Connect", "Planned Integration", "VO2 Max, Stress Index, Pulse Ox")
    ]

    for name, status, metrics in devices:
        st.markdown(
            f"""
            <div class="aegis-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <h4 style="margin:0;">{name}</h4>
                        <p style="font-size:0.85rem; color:#64748b; margin:0.25rem 0 0 0;">Supported telemetry: {metrics}</p>
                    </div>
                    <span class="badge-demo">{status}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("### Data Pipeline Architecture")
    st.code(
        """
        [Wearable Sensors] -> [Native Health SDK] -> [Aegis OAuth Gateway] -> [Data Layer] -> [Risk Analytics]
        """,
        language="text"
    )

    render_disclaimer()
