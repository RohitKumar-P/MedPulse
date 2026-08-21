DISEASE_DISPLAY_NAMES = {
    "diabetes": "Diabetes risk",
    "hypertension": "High blood pressure risk",
    "heart_disease": "Heart health risk",
    "liver_disease": "Liver health risk",
    "chronic_kidney_disease": "Kidney health risk",
    "stroke_risk": "Stroke risk",
    "breast_cancer": "Breast health screening",
    "parkinsons": "Parkinson's disease screening",
    "thyroid": "Thyroid disorder screening",
    "anemia": "Anemia screening",
}

FEATURE_DISPLAY_NAMES = {
    "bmi": "body weight relative to height",
    "glucose": "blood sugar level",
    "blood_pressure": "blood pressure",
    "pregnancies": "number of previous pregnancies",
    "diabetes_pedigree": "family history of diabetes",
    "age": "age",
    "sex": "sex",
    "Hemoglobin": "hemoglobin level",
    "MCH": "red blood cell hemoglobin measurement",
    "MCHC": "red blood cell hemoglobin concentration",
    "MCV": "red blood cell size",
    "sbp_mean": "average upper blood pressure",
    "dbp_mean": "average lower blood pressure",
    "RIAGENDR": "sex",
    "RIDAGEYR": "age",
}

REPORT_REQUIRED_FEATURES = {
    "anemia": [
        "Hemoglobin",
        "MCH",
        "MCHC",
        "MCV"
    ],
    "liver_disease": [],
    "chronic_kidney_disease": [],
}

def disease_name(value):
    return DISEASE_DISPLAY_NAMES.get(
        value,
        value.replace("_", " ").title()
    )

def feature_name(value):
    return FEATURE_DISPLAY_NAMES.get(
        value,
        value.replace("_", " ").replace("-", " ").title()
    )
