import os

APP_NAME = "AEGIS HEALTH AI"
TAGLINE = "Predict. Prevent. Protect."
VERSION = "v1.2.4-beta"

DEFAULT_API_URL = "http://127.0.0.1:8000"
API_BASE_URL = os.getenv("AEGIS_API_BASE_URL", DEFAULT_API_URL)
API_TIMEOUT = int(os.getenv("AEGIS_API_TIMEOUT", "8"))

LEGAL_DISCLAIMER = (
    "This platform provides AI-based screening estimates for educational and preventive-health "
    "purposes only and does not constitute a medical diagnosis. Consult a qualified healthcare "
    "professional for clinical decisions."
)

DISEASE_MODELS = {
    "heart": {
        "name": "Cardiovascular Risk",
        "endpoint": "/predict/heart",
        "category": "Cardiovascular",
        "features": {
            "age": {"label": "Age (years)", "type": "number", "default": 52, "min": 18, "max": 120},
            "sex": {"label": "Sex", "type": "select", "options": [("Male", 1), ("Female", 0)]},
            "cp": {"label": "Chest Pain Type", "type": "select", "options": [("Typical Angina", 0), ("Atypical Angina", 1), ("Non-anginal Pain", 2), ("Asymptomatic", 3)]},
            "trestbps": {"label": "Resting Blood Pressure (mmHg)", "type": "number", "default": 128, "min": 80, "max": 220},
            "chol": {"label": "Serum Cholesterol (mg/dL)", "type": "number", "default": 212, "min": 100, "max": 600},
            "fbs": {"label": "Fasting Blood Sugar > 120 mg/dL", "type": "select", "options": [("No", 0), ("Yes", 1)]},
            "restecg": {"label": "Resting ECG Results", "type": "select", "options": [("Normal", 0), ("ST-T Wave Abnormality", 1), ("Left Ventricular Hypertrophy", 2)]},
            "thalach": {"label": "Maximum Heart Rate Achieved", "type": "number", "default": 150, "min": 60, "max": 220},
            "exang": {"label": "Exercise Induced Angina", "type": "select", "options": [("No", 0), ("Yes", 1)]},
            "oldpeak": {"label": "ST Depression Induced by Exercise", "type": "float", "default": 1.0, "min": 0.0, "max": 10.0, "step": 0.1},
            "slope": {"label": "Slope of Peak Exercise ST Segment", "type": "select", "options": [("Upsloping", 0), ("Flat", 1), ("Downsloping", 2)]},
            "ca": {"label": "Major Vessels Colored by Fluoroscopy", "type": "select", "options": [("0", 0), ("1", 1), ("2", 2), ("3", 3)]},
            "thal": {"label": "Thalassemia", "type": "select", "options": [("Normal", 1), ("Fixed Defect", 2), ("Reversible Defect", 3)]}
        }
    },
    "diabetes": {
        "name": "Diabetes Risk",
        "endpoint": "/predict/diabetes",
        "category": "Endocrine",
        "features": {
            "pregnancies": {"label": "Pregnancies", "type": "number", "default": 1, "min": 0, "max": 20},
            "glucose": {"label": "Plasma Glucose Concentration (2h OGTT)", "type": "number", "default": 118, "min": 40, "max": 300},
            "blood_pressure": {"label": "Diastolic Blood Pressure (mmHg)", "type": "number", "default": 72, "min": 40, "max": 140},
            "skin_thickness": {"label": "Triceps Skin Fold Thickness (mm)", "type": "number", "default": 19, "min": 0, "max": 99},
            "insulin": {"label": "2-Hour Serum Insulin (mu U/ml)", "type": "number", "default": 85, "min": 0, "max": 900},
            "bmi": {"label": "Body Mass Index (BMI)", "type": "float", "default": 27.4, "min": 10.0, "max": 70.0, "step": 0.1},
            "dpf": {"label": "Diabetes Pedigree Function", "type": "float", "default": 0.42, "min": 0.05, "max": 2.5, "step": 0.01},
            "age": {"label": "Age (years)", "type": "number", "default": 34, "min": 18, "max": 120}
        }
    },
    "hypertension": {
        "name": "Hypertension Screening",
        "endpoint": "/predict/hypertension",
        "category": "Cardiovascular",
        "features": {
            "sys_bp": {"label": "Systolic Blood Pressure (mmHg)", "type": "number", "default": 135, "min": 80, "max": 240},
            "dia_bp": {"label": "Diastolic Blood Pressure (mmHg)", "type": "number", "default": 88, "min": 50, "max": 150},
            "bmi": {"label": "Body Mass Index", "type": "float", "default": 28.1, "min": 12.0, "max": 60.0, "step": 0.1},
            "salt_intake": {"label": "Dietary Sodium Intake", "type": "select", "options": [("Low", 0), ("Moderate", 1), ("High", 2)]},
            "physical_activity": {"label": "Weekly Activity (hours)", "type": "number", "default": 2, "min": 0, "max": 30}
        }
    },
    "anemia": {
        "name": "Anemia Screening",
        "endpoint": "/predict/anemia",
        "category": "Hematology",
        "features": {
            "gender": {"label": "Gender", "type": "select", "options": [("Male", 0), ("Female", 1)]},
            "hemoglobin": {"label": "Hemoglobin Level (g/dL)", "type": "float", "default": 12.5, "min": 3.0, "max": 20.0, "step": 0.1},
            "mch": {"label": "Mean Corpuscular Hemoglobin (pg)", "type": "float", "default": 27.0, "min": 10.0, "max": 50.0, "step": 0.1},
            "mchc": {"label": "MCH Concentration (g/dL)", "type": "float", "default": 32.0, "min": 15.0, "max": 45.0, "step": 0.1},
            "mcv": {"label": "Mean Corpuscular Volume (fL)", "type": "float", "default": 85.0, "min": 50.0, "max": 120.0, "step": 0.1}
        }
    },
    "breast_cancer": {
        "name": "Breast Cancer Risk",
        "endpoint": "/predict/breast-cancer",
        "category": "Oncology",
        "features": {
            "radius_mean": {"label": "Radius Mean", "type": "float", "default": 14.1, "min": 5.0, "max": 35.0, "step": 0.1},
            "texture_mean": {"label": "Texture Mean", "type": "float", "default": 19.2, "min": 5.0, "max": 40.0, "step": 0.1},
            "perimeter_mean": {"label": "Perimeter Mean", "type": "float", "default": 91.9, "min": 40.0, "max": 200.0, "step": 0.1},
            "area_mean": {"label": "Area Mean", "type": "float", "default": 654.8, "min": 100.0, "max": 2500.0, "step": 1.0},
            "smoothness_mean": {"label": "Smoothness Mean", "type": "float", "default": 0.096, "min": 0.01, "max": 0.25, "step": 0.001}
        }
    },
    "ckd": {
        "name": "Chronic Kidney Disease",
        "endpoint": "/predict/ckd",
        "category": "Renal",
        "features": {
            "age": {"label": "Age", "type": "number", "default": 48, "min": 1, "max": 110},
            "bp": {"label": "Blood Pressure (mmHg)", "type": "number", "default": 80, "min": 50, "max": 180},
            "sg": {"label": "Specific Gravity", "type": "select", "options": [("1.005", 1.005), ("1.010", 1.010), ("1.015", 1.015), ("1.020", 1.020), ("1.025", 1.025)]},
            "al": {"label": "Albumin", "type": "select", "options": [("0", 0), ("1", 1), ("2", 2), ("3", 3), ("4", 4)]},
            "sc": {"label": "Serum Creatinine (mg/dL)", "type": "float", "default": 1.2, "min": 0.1, "max": 15.0, "step": 0.1}
        }
    },
    "liver": {
        "name": "Liver Disease Screening",
        "endpoint": "/predict/liver",
        "category": "Hepatic",
        "features": {
            "age": {"label": "Age", "type": "number", "default": 45, "min": 4, "max": 100},
            "gender": {"label": "Gender", "type": "select", "options": [("Male", 1), ("Female", 0)]},
            "total_bilirubin": {"label": "Total Bilirubin (mg/dL)", "type": "float", "default": 0.9, "min": 0.1, "max": 30.0, "step": 0.1},
            "direct_bilirubin": {"label": "Direct Bilirubin (mg/dL)", "type": "float", "default": 0.3, "min": 0.1, "max": 15.0, "step": 0.1},
            "alkphos": {"label": "Alkaline Phosphatase (IU/L)", "type": "number", "default": 198, "min": 50, "max": 2000}
        }
    },
    "parkinsons": {
        "name": "Parkinson's Risk Assessment",
        "endpoint": "/predict/parkinsons",
        "category": "Neurology",
        "features": {
            "fo": {"label": "MDVP:Fo (Hz) - Vocal Pitch", "type": "float", "default": 154.2, "min": 80.0, "max": 260.0, "step": 0.1},
            "fhi": {"label": "MDVP:Fhi (Hz) - Max Pitch", "type": "float", "default": 197.1, "min": 100.0, "max": 600.0, "step": 0.1},
            "flo": {"label": "MDVP:Flo (Hz) - Min Pitch", "type": "float", "default": 116.3, "min": 50.0, "max": 240.0, "step": 0.1},
            "jitter_percent": {"label": "MDVP:Jitter (%)", "type": "float", "default": 0.006, "min": 0.0001, "max": 0.05, "step": 0.0001},
            "shimmer": {"label": "MDVP:Shimmer", "type": "float", "default": 0.029, "min": 0.001, "max": 0.2, "step": 0.001}
        }
    },
    "stroke": {
        "name": "Stroke Risk Assessment",
        "endpoint": "/predict/stroke",
        "category": "Cerebrovascular",
        "features": {
            "age": {"label": "Age", "type": "number", "default": 61, "min": 18, "max": 110},
            "hypertension": {"label": "Hypertension History", "type": "select", "options": [("No", 0), ("Yes", 1)]},
            "heart_disease": {"label": "Heart Disease History", "type": "select", "options": [("No", 0), ("Yes", 1)]},
            "avg_glucose": {"label": "Average Glucose Level", "type": "float", "default": 106.1, "min": 50.0, "max": 300.0, "step": 0.1},
            "bmi": {"label": "BMI", "type": "float", "default": 28.8, "min": 10.0, "max": 60.0, "step": 0.1}
        }
    },
    "thyroid": {
        "name": "Thyroid Dysfunction",
        "endpoint": "/predict/thyroid",
        "category": "Endocrine",
        "features": {
            "age": {"label": "Age", "type": "number", "default": 41, "min": 1, "max": 100},
            "sex": {"label": "Sex", "type": "select", "options": [("Female", 0), ("Male", 1)]},
            "tsh": {"label": "TSH Level (mIU/L)", "type": "float", "default": 2.1, "min": 0.01, "max": 100.0, "step": 0.01},
            "t3": {"label": "T3 Level (nmol/L)", "type": "float", "default": 2.0, "min": 0.1, "max": 10.0, "step": 0.1},
            "tt4": {"label": "TT4 Level (nmol/L)", "type": "float", "default": 109.0, "min": 10.0, "max": 300.0, "step": 1.0}
        }
    }
}
