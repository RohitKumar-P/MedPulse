import streamlit as st
import config
from components.ui import render_header, render_disclaimer
from services.api_client import AegisAPIClient

def render_screening():
    render_header("AI Health Screening", subtitle="Select a disease model and input objective clinical metrics for automated risk estimation.", category="Screening")

    selected_key = st.selectbox(
        "Select Health Risk Category",
        options=list(config.DISEASE_MODELS.keys()),
        format_func=lambda x: f"{config.DISEASE_MODELS[x]['name']} ({config.DISEASE_MODELS[x]['category']})"
    )

    model_info = config.DISEASE_MODELS[selected_key]
    st.info(f"**Selected Model:** {model_info['name']} | **Endpoint:** {model_info['endpoint']}")

    st.markdown("#### Input Clinical Features")
    st.caption("Provide precise clinical measurements or recent lab values. Do not substitute with subjective estimates.")

    payload = {}
    features = model_info["features"]
    
    cols = st.columns(2)
    idx = 0
    
    with st.form(key=f"form_{selected_key}"):
        for f_key, f_cfg in features.items():
            col = cols[idx % 2]
            idx += 1
            with col:
                if f_cfg["type"] == "number":
                    payload[f_key] = st.number_input(
                        f_cfg["label"],
                        min_value=f_cfg.get("min", 0),
                        max_value=f_cfg.get("max", 1000),
                        value=f_cfg.get("default", 0)
                    )
                elif f_cfg["type"] == "float":
                    payload[f_key] = st.number_input(
                        f_cfg["label"],
                        min_value=f_cfg.get("min", 0.0),
                        max_value=f_cfg.get("max", 1000.0),
                        value=f_cfg.get("default", 0.0),
                        step=f_cfg.get("step", 0.1)
                    )
                elif f_cfg["type"] == "select":
                    options = f_cfg["options"]
                    choice = st.selectbox(
                        f_cfg["label"],
                        options=[opt[0] for opt in options]
                    )
                    val = next(opt[1] for opt in options if opt[0] == choice)
                    payload[f_key] = val

        submit = st.form_submit_button("Execute AI Screening", type="primary", use_container_width=True)

    if submit:
        with st.spinner("Analyzing clinical data via Aegis AI Engine..."):
            client = AegisAPIClient()
            success, result = client.predict(selected_key, payload)

            if not success:
                st.warning("Primary backend offline or unreachable. Engaging local fallback deterministic engine.")
                result = client.run_fallback_simulation(selected_key, payload)
                st.session_state["demo_mode"] = True

            st.session_state["latest_result"] = result
            st.session_state["latest_model_key"] = selected_key
            
            history = st.session_state.get("screening_history", [])
            history.insert(0, {
                "Date": "18 Aug 2026",
                "Assessment": model_info["name"],
                "Risk Level": result.get("risk_level", "UNKNOWN"),
                "Score": f"{result.get('risk_score', 0)}%",
                "Status": "Completed"
            })
            st.session_state["screening_history"] = history
            
            st.session_state["current_page"] = "results"
            st.rerun()

    render_disclaimer()
