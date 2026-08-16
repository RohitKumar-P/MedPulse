CONDITION_REGISTRY = {
    "endocrine_metabolic": [
        "Hyperglycemia",
        "Diabetes Type 1",
        "Diabetes Type 2",
        "Diabetes Insipidus",
        "Hypothyroidism",
        "Hyperthyroidism",
        "Anemia",
        "Iron Deficiency Anemia"
    ],

    "cardiovascular": [
        "High Blood Pressure",
        "Hypertension",
        "Coronary Artery Disease",
        "Heart Failure",
        "Atrial Fibrillation",
        "Heart Attack",
        "Stroke"
    ],

    "respiratory": [
        "Asthma",
        "Chronic Obstructive Pulmonary Disease",
        "Pneumonia",
        "Influenza",
        "COVID-19",
        "Tuberculosis"
    ],

    "neurological": [
        "Migraine",
        "Epilepsy",
        "Meningitis",
        "Parkinson's Disease"
    ],

    "gastrointestinal": [
        "Gastroesophageal Reflux Disease",
        "Irritable Bowel Syndrome",
        "Peptic Ulcer",
        "Gastroenteritis",
        "Appendicitis",
        "Gallstones"
    ],

    "renal_urinary": [
        "Urinary Tract Infection",
        "Kidney Stones",
        "Chronic Kidney Disease"
    ],

    "allergy_immune": [
        "Allergic Rhinitis",
        "Food Allergy",
        "Drug Allergy",
        "Anaphylaxis",
        "Eczema"
    ],

    "infectious": [
        "Common Cold",
        "Dengue",
        "Malaria",
        "Typhoid Fever",
        "Hepatitis A",
        "Hepatitis B"
    ],

    "dermatology": [
        "Psoriasis",
        "Acne",
        "Hives"
    ]
}


def build_condition_index():

    index = {}

    for category, conditions in CONDITION_REGISTRY.items():

        for condition in conditions:

            index[
                condition.lower().strip()
            ] = {
                "name": condition,
                "category": category
            }

    return index


CONDITIONS = build_condition_index()


def get_condition(title):

    return CONDITIONS.get(
        title.lower().strip()
    )


def is_curated_condition(title):

    return get_condition(title) is not None


def get_category(title):

    condition = get_condition(title)

    if not condition:
        return None

    return condition["category"]


def list_conditions():

    return [
        value
        for value in CONDITIONS.values()
    ]


# Extended disease prediction registry
EXTENDED_CONDITIONS = {
    "hypertension": {
        "display_name": "Hypertension",
        "status": "planned"
    },
    "chronic_kidney_disease": {
        "display_name": "Chronic Kidney Disease",
        "status": "planned"
    },
    "liver_disease": {
        "display_name": "Liver Disease",
        "status": "planned"
    },
    "stroke": {
        "display_name": "Stroke",
        "status": "planned"
    },
    "thyroid": {
        "display_name": "Thyroid Disorder",
        "status": "planned"
    }
}
