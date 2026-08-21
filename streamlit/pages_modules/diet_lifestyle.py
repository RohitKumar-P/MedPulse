import streamlit as st
from components.ui import render_header, render_disclaimer

def render_diet():
    render_header("Diet & Lifestyle Guidance", subtitle="General preventive wellness strategies based on your risk screening profile.", category="Preventive Guidance")

    st.markdown(
        """
        <div class="aegis-card" style="border-left: 4px solid #0284c7;">
            <h4 style="margin:0 0 0.5rem 0;">Guidance Scope</h4>
            <p style="font-size:0.85rem; color:#64748b; margin:0;">
                These suggestions are general wellness recommendations intended to support cardiovascular and metabolic health. They are not medical prescriptions or customized medical nutrition therapy.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Recommended Foods")
        st.markdown("- **Leafy Greens:** Spinach, kale, and swiss chard for dietary nitrates.")
        st.markdown("- **Whole Grains:** Oats, quinoa, and brown rice for soluble fiber.")
        st.markdown("- **Lean Proteins:** Wild-caught fish, legumes, and poultry.")
        st.markdown("- **Healthy Fats:** Extra virgin olive oil, avocados, and walnuts.")

    with c2:
        st.markdown("#### Dietary Modifications")
        st.markdown("- **Sodium Intake:** Aim for under 2,000 mg daily to support optimal blood pressure.")
        st.markdown("- **Added Sugars:** Limit refined sugars and sugar-sweetened beverages.")
        st.markdown("- **Ultra-Processed Foods:** Reduce intake of pre-packaged snacks and processed meats.")

    st.markdown("---")
    st.markdown("#### Lifestyle & Physical Activity")
    st.markdown("- **Aerobic Exercise:** 150 minutes of moderate-intensity activity per week.")
    st.markdown("- **Sleep Hygiene:** Maintain 7 to 9 hours of continuous restful sleep daily.")
    st.markdown("- **Hydration:** Target 2.5 to 3.5 liters of water daily depending on activity level.")

    render_disclaimer()
