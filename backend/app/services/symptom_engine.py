import re

from app.data.symptoms import SYMPTOMS
import app.data.symptom_expansion

from app.data.evidence import (
    EVIDENCE_RULES,
    EVIDENCE_SOURCES
)

from app.services.evidence_engine import (
    build_evidence
)


def normalize(text):
    return re.sub(
        r"\s+",
        " ",
        text.lower().strip()
    )


def detect_symptoms(text):

    text = normalize(text)

    detected = []

    for symptom, phrases in SYMPTOMS.items():

        matches = []

        for phrase in phrases:

            if phrase in text:
                matches.append(phrase)

        if matches:

            detected.append({
                "symptom": symptom,
                "matched_phrases": matches
            })

    return detected


def emergency_analysis(symptoms):

    names = {
        item["symptom"]
        for item in symptoms
    }

    rules = [

        ({"chest_pain"}, "severe_chest_pain"),

        (
            {"breathing_difficulty"},
            "severe_shortness_of_breath"
        ),

        (
            {"speech_problem"},
            "sudden_speech_problem"
        ),

        (
            {"one_sided_weakness"},
            "sudden_one_sided_weakness"
        ),

        (
            {"vision_problem"},
            "sudden_vision_problem"
        ),

        (
            {"severe_headache"},
            "sudden_severe_headache"
        ),

        ({"fainting"}, "fainting"),

        ({"seizure"}, "seizure"),

        (
            {
                "lip_tongue_swelling",
                "breathing_difficulty"
            },
            "anaphylaxis_breathing"
        ),

        (
            {
                "lip_tongue_swelling",
                "trouble_swallowing"
            },
            "anaphylaxis_airway"
        ),

        (
            {
                "facial_swelling",
                "breathing_difficulty"
            },
            "anaphylaxis_swelling"
        ),

        (
            {
                "hives",
                "breathing_difficulty"
            },
            "anaphylaxis_breathing"
        )
    ]

    alerts = []

    for required, rule in rules:

        if not required.issubset(names):
            continue

        evidence_rule = EVIDENCE_RULES.get(rule)

        if not evidence_rule:
            continue

        source = EVIDENCE_SOURCES.get(
            evidence_rule["source"]
        )

        if not source:
            continue

        alerts.append({
            "rule": rule,
            "action": evidence_rule["action"],
            "evidence": {
                "title": source["title"],
                "organization": source["organization"],
                "url": source["url"]
            }
        })

    if alerts:

        return {
            "status": "urgent",
            "message": (
                "Reported symptoms match "
                "published warning signs. "
                "Aegis cannot determine the cause."
            ),
            "alerts": alerts
        }

    return {
        "status": "no_emergency_rule_triggered",
        "message": (
            "No configured emergency rule "
            "was triggered. This does not "
            "rule out a serious condition."
        ),
        "alerts": []
    }


async def analyze_symptoms(text):

    symptoms = detect_symptoms(text)

    emergency = emergency_analysis(
        symptoms
    )

    evidence = await build_evidence(
        symptoms,
        text
    )

    return {
        "input_text": text,
        "detected_symptoms": symptoms,
        "emergency": emergency,
        "evidence": evidence,
        "clinical_interpretation": {
            "possible_conditions": [],
            "status": "not_determined",
            "reason": (
                "Symptoms alone are not "
                "sufficient evidence for an "
                "Aegis diagnosis."
            )
        },
        "evidence_policy": {
            "unsupported_claims": False,
            "diagnosis_from_symptoms": False,
            "treatment_recommendation": False,
            "missing_information_is_reported": True,
            "source_required": True
        }
    }
