CLINICAL_KNOWLEDGE = {

    "Hyperglycemia": {
        "plain_name": "High blood sugar",
        "category": "endocrine_metabolic",
        "evidence_type": "physiological_state",
        "diagnosis_from_symptoms": False,
        "requires_clinical_confirmation": True,
        "cannot_distinguish": [
            "Diabetes Type 1",
            "Diabetes Type 2",
            "Other causes of elevated blood glucose"
        ]
    },

    "Diabetes Type 1": {
        "plain_name": "Type 1 diabetes",
        "category": "endocrine_metabolic",
        "evidence_type": "condition",
        "diagnosis_from_symptoms": False,
        "requires_clinical_confirmation": True,
        "cannot_distinguish": [
            "Diabetes Type 2"
        ]
    },

    "Diabetes Type 2": {
        "plain_name": "Type 2 diabetes",
        "category": "endocrine_metabolic",
        "evidence_type": "condition",
        "diagnosis_from_symptoms": False,
        "requires_clinical_confirmation": True,
        "cannot_distinguish": [
            "Diabetes Type 1"
        ]
    },

    "Diabetes Insipidus": {
        "plain_name": "Diabetes insipidus",
        "category": "endocrine_metabolic",
        "evidence_type": "condition",
        "diagnosis_from_symptoms": False,
        "requires_clinical_confirmation": True,
        "cannot_distinguish": []
    }
}


def get_clinical_knowledge(
    condition
):

    return CLINICAL_KNOWLEDGE.get(
        condition
    )


def has_clinical_knowledge(
    condition
):

    return condition in CLINICAL_KNOWLEDGE
