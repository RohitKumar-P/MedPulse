import re


CANONICAL_SYMPTOMS = {

    "excessive_thirst": {
        "excessive thirst",
        "extreme thirst",
        "very thirsty",
        "constant thirst",
        "thirsty all the time",
        "drinking water constantly"
    },

    "frequent_urination": {
        "frequent urination",
        "urinating frequently",
        "pee frequently",
        "peeing frequently",
        "urinating often",
        "peeing often"
    },

    "fatigue": {
        "fatigue",
        "feeling tired",
        "tiredness",
        "extreme tiredness",
        "low energy",
        "lack of energy"
    },

    "blurred_vision": {
        "blurred vision",
        "blurry vision",
        "vision is blurry",
        "difficulty seeing clearly"
    },

    "chest_pain": {
        "chest pain",
        "pain in chest",
        "chest discomfort"
    },

    "breathing_difficulty": {
        "difficulty breathing",
        "shortness of breath",
        "breathing difficulty",
        "trouble breathing",
        "cannot breathe properly"
    },

    "fever": {
        "fever",
        "high temperature",
        "raised temperature"
    },

    "cough": {
        "cough",
        "coughing"
    },

    "headache": {
        "headache",
        "head pain"
    },

    "dizziness": {
        "dizziness",
        "feeling dizzy",
        "lightheaded",
        "light headed"
    },

    "nausea": {
        "nausea",
        "feeling nauseous",
        "feeling sick"
    },

    "vomiting": {
        "vomiting",
        "throwing up",
        "threw up"
    },

    "diarrhea": {
        "diarrhea",
        "loose stools",
        "loose motions"
    },

    "abdominal_pain": {
        "abdominal pain",
        "stomach pain",
        "belly pain",
        "pain in my abdomen"
    },

    "sore_throat": {
        "sore throat",
        "throat pain",
        "painful throat"
    },

    "runny_nose": {
        "runny nose",
        "nose running"
    },

    "nasal_congestion": {
        "blocked nose",
        "stuffy nose",
        "nasal congestion"
    },

    "sneezing": {
        "sneezing",
        "sneezing repeatedly"
    },

    "itchy_eyes": {
        "itchy eyes",
        "eyes are itchy"
    },

    "skin_rash": {
        "skin rash",
        "rash",
        "skin irritation"
    },

    "swelling": {
        "swelling",
        "swollen"
    },

    "joint_pain": {
        "joint pain",
        "painful joints"
    },

    "muscle_pain": {
        "muscle pain",
        "body aches",
        "muscle aches"
    },

    "speech_problem": {
        "cannot speak",
        "difficulty speaking",
        "speech problem",
        "slurred speech",
        "trouble speaking"
    },

    "facial_drooping": {
        "face drooping",
        "facial drooping",
        "drooping face"
    }
}


def normalize_text(text):

    text = str(
        text or ""
    ).lower().strip()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text


LOOKUP = {}

for canonical, phrases in CANONICAL_SYMPTOMS.items():

    for phrase in phrases:

        LOOKUP[
            normalize_text(phrase)
        ] = canonical


def canonicalize_symptom(
    symptom_name
):

    normalized = normalize_text(
        symptom_name
    )

    if normalized in LOOKUP:

        return LOOKUP[
            normalized
        ]

    for phrase, canonical in LOOKUP.items():

        if (
            phrase in normalized
            or normalized in phrase
        ):

            return canonical

    return None


def canonicalize_extraction(
    extraction
):

    result = dict(
        extraction
    )

    symptoms = []

    seen = set()

    for symptom in extraction.get(
        "symptoms",
        []
    ):

        canonical = canonicalize_symptom(
            symptom.get("name")
        )

        if not canonical:
            continue

        if canonical in seen:
            continue

        item = dict(
            symptom
        )

        item["name"] = canonical

        # Do not convert wording intensity
        # into clinical severity.
        item["severity"] = (
            symptom.get("severity")
            if symptom.get("severity")
            in {
                "mild",
                "moderate",
                "severe"
            }
            else "unknown"
        )

        symptoms.append(
            item
        )

        seen.add(
            canonical
        )

    result[
        "symptoms"
    ] = symptoms

    return result
