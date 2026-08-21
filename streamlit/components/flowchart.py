import streamlit as st

def render_aegis_flowchart():
    st.markdown(
        """
        <div style="padding: 1rem 0;">
            <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 8px;">
                <div class="flow-node" style="flex: 1; min-width: 110px;">User Input<br/><span style="font-size:0.75rem; color:#64748b;">Clinical/Vitals</span></div>
                <div class="flow-arrow">&rarr;</div>
                <div class="flow-node" style="flex: 1; min-width: 110px;">Health Data<br/><span style="font-size:0.75rem; color:#64748b;">Validation Engine</span></div>
                <div class="flow-arrow">&rarr;</div>
                <div class="flow-node" style="flex: 1; min-width: 110px;">AI Model<br/><span style="font-size:0.75rem; color:#64748b;">FastAPI Service</span></div>
                <div class="flow-arrow">&rarr;</div>
                <div class="flow-node" style="flex: 1; min-width: 110px;">Risk Estimation<br/><span style="font-size:0.75rem; color:#64748b;">Probability Index</span></div>
                <div class="flow-arrow">&rarr;</div>
                <div class="flow-node" style="flex: 1; min-width: 110px;">Health Insights<br/><span style="font-size:0.75rem; color:#64748b;">Feature Weights</span></div>
                <div class="flow-arrow">&rarr;</div>
                <div class="flow-node" style="flex: 1; min-width: 110px;">Preventive Guidance<br/><span style="font-size:0.75rem; color:#64748b;">Lifestyle Direction</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
