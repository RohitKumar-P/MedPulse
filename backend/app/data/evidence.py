EVIDENCE_SOURCES = {
    "medlineplus_emergency": {
        "title": "When to use the emergency room - adult",
        "organization": "MedlinePlus / U.S. National Library of Medicine",
        "url": "https://medlineplus.gov/ency/patientinstructions/000593.htm",
        "accessed": "2026-08-14"
    },
    "medlineplus_stroke": {
        "title": "Stroke",
        "organization": "MedlinePlus / U.S. National Library of Medicine",
        "url": "https://medlineplus.gov/stroke.html",
        "accessed": "2026-08-14"
    },
    "medlineplus_heart_warning": {
        "title": "Warning signs and symptoms of heart disease",
        "organization": "MedlinePlus / U.S. National Library of Medicine",
        "url": "https://medlineplus.gov/ency/patientinstructions/000775.htm",
        "accessed": "2026-08-14"
    },
    "who_ai_health": {
        "title": "WHO calls for safe and ethical AI for health",
        "organization": "World Health Organization",
        "url": "https://www.who.int/news/item/16-05-2023-who-calls-for-safe-and-ethical-ai-for-health",
        "accessed": "2026-08-14"
    }
}


EVIDENCE_RULES = {
    "severe_chest_pain": {
        "source": "medlineplus_emergency",
        "action": "urgent_medical_attention"
    },
    "severe_shortness_of_breath": {
        "source": "medlineplus_emergency",
        "action": "urgent_medical_attention"
    },
    "sudden_speech_problem": {
        "source": "medlineplus_stroke",
        "action": "urgent_medical_attention"
    },
    "sudden_one_sided_weakness": {
        "source": "medlineplus_stroke",
        "action": "urgent_medical_attention"
    },
    "sudden_vision_problem": {
        "source": "medlineplus_stroke",
        "action": "urgent_medical_attention"
    },
    "sudden_severe_headache": {
        "source": "medlineplus_stroke",
        "action": "urgent_medical_attention"
    },
    "fainting": {
        "source": "medlineplus_emergency",
        "action": "urgent_medical_attention"
    },
    "seizure": {
        "source": "medlineplus_emergency",
        "action": "urgent_medical_attention"
    }
}
from app.data.evidence import EVIDENCE_RULES

EVIDENCE_RULES.update({

    "anaphylaxis_airway": {
        "source": "medlineplus_emergency",
        "action": "urgent_medical_attention"
    },

    "anaphylaxis_swelling": {
        "source": "medlineplus_emergency",
        "action": "urgent_medical_attention"
    },

    "anaphylaxis_breathing": {
        "source": "medlineplus_emergency",
        "action": "urgent_medical_attention"
    }
})
