import streamlit as st

# ---------------------------------------------------------
# AI-Driven Early Disease Detection Platform
# Streamlit frontend prototype
# ---------------------------------------------------------

st.set_page_config(
    page_title="MediScan AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown("""
<style>
    .main {
        background-color: #f7f9fc;
    }

    .hero {
        padding: 28px 32px;
        border-radius: 18px;
        background: linear-gradient(135deg, #0f766e, #2563eb);
        color: white;
        margin-bottom: 24px;
    }

    .hero h1 {
        font-size: 42px;
        margin-bottom: 8px;
    }

    .hero p {
        font-size: 18px;
        opacity: 0.92;
    }

    .card {
        background: white;
        padding: 22px;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        margin-bottom: 18px;
    }

    .result-card {
        background: #ffffff;
        padding: 28px;
        border-radius: 18px;
        border: 1px solid #dbeafe;
        box-shadow: 0 4px 18px rgba(0,0,0,0.05);
    }

    .small-muted {
        color: #64748b;
        font-size: 14px;
    }

    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        min-height: 45px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ---------- Session state ----------
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "prediction" not in st.session_state:
    st.session_state.prediction = None


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 🩺 MediScan AI")
    st.caption("Early disease risk assessment")

    st.divider()

    if st.button("🏠 Dashboard"):
        st.session_state.page = "Dashboard"

    if st.button("👤 Patient Assessment"):
        st.session_state.page = "Assessment"

    if st.button("📊 Prediction"):
        st.session_state.page = "Prediction"

    if st.button("ℹ️ About"):
        st.session_state.page = "About"

    st.divider()
    st.caption("Prototype for hackathon demonstration")
    st.caption("Not a medical diagnosis.")


# ---------- Dashboard ----------
if st.session_state.page == "Dashboard":

    st.markdown("""
    <div class="hero">
        <h1>🩺 MediScan AI</h1>
        <p>AI-assisted early disease risk detection from patient symptoms and medical history.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="card">
            <h3>👤 Patient Data</h3>
            <p>Enter basic demographic information, symptoms and medical history.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
            <h3>🤖 AI Analysis</h3>
            <p>Your trained machine-learning model can analyse the submitted features.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="card">
            <h3>📊 Risk Result</h3>
            <p>Display the predicted disease/risk category and relevant information.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### How it works")

    steps = [
        ("1", "Enter patient information"),
        ("2", "Select symptoms"),
        ("3", "Submit the assessment"),
        ("4", "ML model generates a prediction"),
        ("5", "Review the result and suggested next step"),
    ]

    for number, text in steps:
        st.markdown(f"**{number}.** {text}")

    st.info(
        "This is a hackathon prototype. The prediction shown by this interface "
        "should not be used as a real medical diagnosis."
    )

    if st.button("Start Patient Assessment", type="primary"):
        st.session_state.page = "Assessment"
        st.rerun()


# ---------- Assessment ----------
elif st.session_state.page == "Assessment":

    st.title("👤 Patient Assessment")
    st.write("Enter the patient's information below.")

    with st.form("patient_form"):

        st.markdown("### Basic Information")

        col1, col2, col3 = st.columns(3)

        with col1:
            name = st.text_input("Patient name")

        with col2:
            age = st.number_input("Age", min_value=1, max_value=120, value=25)

        with col3:
            gender = st.selectbox(
                "Gender",
                ["Select", "Female", "Male", "Other", "Prefer not to say"]
            )

        st.markdown("### Symptoms")

        symptom_options = [
            "Fever",
            "Cough",
            "Fatigue",
            "Headache",
            "Nausea",
            "Vomiting",
            "Abdominal pain",
            "Chest pain",
            "Shortness of breath",
            "Dizziness",
            "Joint pain",
            "Skin rash",
            "Weight change",
            "Loss of appetite",
        ]

        symptoms = st.multiselect(
            "Select symptoms",
            symptom_options,
            placeholder="Choose one or more symptoms"
        )

        st.markdown("### Medical History")

        col1, col2 = st.columns(2)

        with col1:
            chronic_conditions = st.multiselect(
                "Existing conditions",
                [
                    "None",
                    "Diabetes",
                    "Hypertension",
                    "Asthma",
                    "Heart disease",
                    "Kidney disease",
                    "Liver disease",
                ],
            )

        with col2:
            family_history = st.selectbox(
                "Relevant family history",
                ["None", "Diabetes", "Heart disease", "Cancer", "Other"]
            )

        st.markdown("### Additional Information")

        notes = st.text_area(
            "Additional notes",
            placeholder="Enter relevant information such as symptom duration..."
        )

        submitted = st.form_submit_button(
            "🔍 Analyse Patient",
            type="primary"
        )

        if submitted:

            if gender == "Select":
                st.error("Please select a gender option.")
            elif len(symptoms) == 0:
                st.error("Please select at least one symptom.")
            else:
                # -------------------------------------------------
                # DEMO PREDICTION
                # Replace this section with your trained ML model.
                #
                # Example:
                # prediction = model.predict(input_dataframe)[0]
                # probability = model.predict_proba(input_dataframe).max()
                # -------------------------------------------------

                symptom_count = len(symptoms)

                if symptom_count >= 5:
                    disease = "Higher-risk symptom pattern"
                    confidence = 78
                elif symptom_count >= 3:
                    disease = "Moderate-risk symptom pattern"
                    confidence = 64
                else:
                    disease = "Lower-risk symptom pattern"
                    confidence = 52

                st.session_state.prediction = {
                    "name": name if name else "Patient",
                    "age": age,
                    "gender": gender,
                    "symptoms": symptoms,
                    "disease": disease,
                    "confidence": confidence,
                    "conditions": chronic_conditions,
                    "family_history": family_history,
                    "notes": notes,
                }

                st.session_state.page = "Prediction"
                st.rerun()


# ---------- Prediction ----------
elif st.session_state.page == "Prediction":

    st.title("📊 Prediction Result")

    result = st.session_state.prediction

    if result is None:
        st.warning("No assessment has been submitted yet.")

        if st.button("Go to Assessment", type="primary"):
            st.session_state.page = "Assessment"
            st.rerun()

    else:
        st.markdown(
            f"""
            <div class="result-card">
                <h2>Assessment for {result["name"]}</h2>
                <p class="small-muted">
                    Age: {result["age"]} &nbsp; | &nbsp;
                    Gender: {result["gender"]}
                </p>
                <hr>
                <h3>Predicted category</h3>
                <h2>🧠 {result["disease"]}</h2>
                <p><strong>Demo confidence:</strong> {result["confidence"]}%</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.progress(result["confidence"] / 100)

        st.markdown("### Reported Symptoms")
        st.write(", ".join(result["symptoms"]))

        st.markdown("### Medical History")
        if result["conditions"]:
            st.write(", ".join(result["conditions"]))
        else:
            st.write("No existing conditions selected.")

        st.markdown("### Recommended Next Step")

        st.warning(
            "This result is only a prototype output. It is not a diagnosis. "
            "A qualified healthcare professional should evaluate symptoms and "
            "medical history before any medical decision is made."
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔄 New Assessment", type="primary"):
                st.session_state.prediction = None
                st.session_state.page = "Assessment"
                st.rerun()

        with col2:
            if st.button("🏠 Back to Dashboard"):
                st.session_state.page = "Dashboard"
                st.rerun()


# ---------- About ----------
elif st.session_state.page == "About":

    st.title("ℹ️ About MediScan AI")

    st.markdown("""
    ### What is MediScan AI?

    MediScan AI is a hackathon prototype designed to demonstrate how
    machine-learning models can assist with early disease-risk assessment.

    ### Planned architecture

    **Patient → Streamlit UI → Feature preprocessing → ML model → Prediction → Result**

    The frontend collects:
    - Age
    - Gender
    - Symptoms
    - Existing medical conditions
    - Family history
    - Additional notes

    The ML team can later connect the trained model to the assessment page.

    ### Important

    This prototype is for demonstration and educational purposes only.
    It must not be treated as a medical diagnostic system.
    """)
