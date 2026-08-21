# MedPulse screening configuration
# Questions are intentionally written in normal language.

SCREENING_QUESTIONS = {
    "general": [
        {
            "id": "age",
            "question": "How old are you?",
            "type": "number",
            "required": True
        },
        {
            "id": "gender",
            "question": "What is your gender?",
            "type": "choice",
            "options": ["Male", "Female"],
            "required": True
        }
    ],

    "hypertension": [
        {
            "id": "blood_pressure",
            "question": "Do you know your recent blood pressure reading?",
            "type": "blood_pressure",
            "required": True
        },
        {
            "id": "bmi",
            "question": "Do you know your height and weight?",
            "type": "height_weight",
            "required": False
        }
    ],

    "anemia": [
        {
            "id": "hemoglobin",
            "question": "Do you have a recent blood test showing your hemoglobin level?",
            "type": "number",
            "required": True
        },
        {
            "id": "tiredness",
            "question": "Have you been feeling unusually tired or weak?",
            "type": "yes_no",
            "required": False
        },
        {
            "id": "dizziness",
            "question": "Have you been feeling dizzy or light-headed?",
            "type": "yes_no",
            "required": False
        }
    ],

    "diabetes": [
        {
            "id": "frequent_urination",
            "question": "Have you been needing to urinate more often than usual?",
            "type": "yes_no",
            "required": False
        },
        {
            "id": "excessive_thirst",
            "question": "Have you been unusually thirsty?",
            "type": "yes_no",
            "required": False
        },
        {
            "id": "blood_glucose",
            "question": "Do you have a recent blood sugar reading?",
            "type": "number",
            "required": False
        }
    ],

    "kidney_disease": [
        {
            "id": "creatinine",
            "question": "Do you have a recent blood test showing your kidney function or creatinine level?",
            "type": "number",
            "required": False
        },
        {
            "id": "swelling",
            "question": "Have you noticed unusual swelling in your legs, feet, hands or face?",
            "type": "yes_no",
            "required": False
        },
        {
            "id": "urine_change",
            "question": "Have you noticed a change in how often you urinate or what your urine looks like?",
            "type": "yes_no",
            "required": False
        }
    ],

    "liver_disease": [
        {
            "id": "jaundice",
            "question": "Have your eyes or skin looked unusually yellow?",
            "type": "yes_no",
            "required": False
        },
        {
            "id": "abdominal_pain",
            "question": "Have you had ongoing pain or discomfort in the upper-right part of your stomach?",
            "type": "yes_no",
            "required": False
        }
    ]
}

OPTIONAL_WARNING = (
    "You can continue without optional information, but providing it "
    "can improve screening accuracy."
)
