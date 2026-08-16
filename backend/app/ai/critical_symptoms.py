import re


CRITICAL_SYMPTOMS = {
    "swelling": ["throat is swelling", "throat swelling", "swelling of the throat"],

    "chest_pain": [
        "chest pain",
        "pain in my chest",
        "pressure in my chest",
        "chest pressure",
        "chest tightness"
    ],

    "breathing_difficulty": [
        "difficulty breathing",
        "trouble breathing",
        "shortness of breath",
        "cannot breathe",
        "can't breathe",
        "breathing difficulty",
        "breathing problems"
    ],

    "facial_drooping": [
        "face is drooping",
        "face drooping",
        "facial drooping",
        "drooping face"
    ],

    "speech_problem": [
        "cannot speak",
        "can't speak",
        "difficulty speaking",
        "trouble speaking",
        "slurred speech",
        "speech problem"
    ],

    "sudden_weakness": [
        "sudden weakness",
        "suddenly weak",
        "weakness on one side",
        "one sided weakness",
        "one-sided weakness"
    ],

    "loss_of_consciousness": [
        "lost consciousness",
        "loss of consciousness",
        "passed out",
        "fainted",
        "unconscious"
    ],

    "seizure": [
        "seizure",
        "having a seizure",
        "had a seizure",
        "seizures",
        "convulsion",
        "convulsions",
        "having convulsions",
        "convulsing"
    ],

    "severe_bleeding": [
        "severe bleeding",
        "heavy bleeding",
        "bleeding heavily",
        "cannot stop bleeding"
    ]
}


NEGATION_PATTERNS = [

    r"\bno\b",
    r"\bnot\b",
    r"\bnever\b",
    r"\bwithout\b",
    r"\bdenies\b",
    r"\bdenied\b",
    r"\bdon't\b",
    r"\bdoesn't\b",
    r"\bdidn't\b",
    r"\bhasn't\b",
    r"\bhaven't\b",
    r"\bhadn't\b",
    r"\bwasn't\b",
    r"\bweren't\b",
    r"\bnone\b"
]


def normalize_text(text):

    text = str(
        text or ""
    ).lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def is_negated(
    text,
    start
):

    window_start = max(
        0,
        start - 80
    )

    context = text[
        window_start:start
    ]

    words = context.split()

    recent_words = words[-8:]

    recent_context = " ".join(
        recent_words
    )

    for pattern in NEGATION_PATTERNS:

        if re.search(
            pattern,
            recent_context
        ):

            return True

    return False


def detect_critical_symptoms(
    text
):

    normalized = normalize_text(
        text
    )

    detected = []

    for symptom, phrases in (
        CRITICAL_SYMPTOMS.items()
    ):

        matches = []

        for phrase in phrases:

            start = normalized.find(
                phrase
            )

            if start == -1:
                continue

            if is_negated(
                normalized,
                start
            ):

                continue

            matches.append(
                phrase
            )

        if matches:

            detected.append({

                "symptom":
                    symptom,

                "matched_phrases":
                    matches,

                "source":
                    "deterministic_safety_layer"

            })

    # Pattern-based emergency condition:
    # throat/tongue swelling + breathing difficulty.
    throat_swelling = any(
        phrase in normalized
        for phrase in [
            "throat swelling",
            "throat is swelling",
            "swelling in my throat",
            "tongue swelling",
            "tongue is swelling"
        ]
    )

    breathing = any(
        item["symptom"]
        == "breathing_difficulty"
        for item in detected
    )

    if (
        throat_swelling
        and breathing
    ):

        detected.append({

            "symptom":
                "severe_allergic_reaction",

            "matched_phrases": [
                "airway/throat swelling with breathing difficulty"
            ],

            "source":
                "deterministic_safety_layer"

        })

    return detected

