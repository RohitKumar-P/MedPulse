import re


SYMPTOM_TERMS = {

    "fatigue": [
        "feeling tired",
        "tired",
        "fatigue",
        "weak",
        "weakness",
        "exhausted"
    ],

    "excessive_thirst": [
        "extremely thirsty",
        "excessive thirst",
        "very thirsty",
        "increased thirst",
        "feeling thirsty",
        "thirsty"
    ],

    "frequent_urination": [
        "urinating frequently",
        "frequent urination",
        "urinating often",
        "peeing often",
        "urinate often",
        "urinating a lot"
    ],

    "blurred_vision": [
        "blurred vision",
        "blurry vision",
        "blurry eyesight",
        "blurred eyesight",
        "blurry eyesight"
    ],

    "chest_pain": [
        "chest pain",
        "pain in the chest"
    ],

    "breathing_difficulty": [
        "difficulty breathing",
        "trouble breathing",
        "shortness of breath",
        "breathing difficulty"
    ],

    "fever": [
        "fever",
        "high temperature"
    ],

    "cough": [
        "cough",
        "coughing"
    ],

    "headache": [
        "headache",
        "head pain"
    ],

    "nausea": [
        "nausea",
        "feeling sick",
        "feel sick"
    ],

    "vomiting": [
        "vomiting",
        "throwing up",
        "threw up"
    ],

    "diarrhea": [
        "diarrhea",
        "loose stools",
        "loose motion"
    ],

    "abdominal_pain": [
        "abdominal pain",
        "stomach pain",
        "belly pain"
    ],

    "dizziness": [
        "dizziness",
        "dizzy",
        "lightheaded"
    ],

    "fainting": [
        "fainting",
        "passed out",
        "loss of consciousness"
    ],

    "speech_problem": [
        "cannot speak",
        "difficulty speaking",
        "slurred speech",
        "speech problem"
    ],

    "facial_drooping": [
        "face drooping",
        "facial drooping",
        "drooping face"
    ],

    "numbness": [
        "numbness",
        "numb",
        "loss of sensation"
    ],

    "rash": [
        "rash",
        "skin rash"
    ],

    "itching": [
        "itching",
        "itchy"
    ],

    "swelling": [
        "swelling",
        "swollen"
    ],

    "joint_pain": [
        "joint pain",
        "painful joints"
    ],

    "muscle_pain": [
        "muscle pain",
        "body aches",
        "muscle aches"
    ],

    "sore_throat": [
        "sore throat",
        "throat pain"
    ],

    "runny_nose": [
        "runny nose",
        "running nose"
    ],

    "nasal_congestion": [
        "blocked nose",
        "stuffy nose",
        "nasal congestion"
    ],

    "palpitations": [
        "heart palpitations",
        "palpitations",
        "racing heart",
        "heart racing"
    ],

    "weight_loss": [
        "unexplained weight loss",
        "losing weight",
        "weight loss"
    ],

    "weight_gain": [
        "weight gain",
        "gaining weight"
    ]
}


SYMPTOM_SECTION_MARKERS = [
    "symptoms include",
    "symptoms may include",
    "symptoms can include",
    "symptoms are",
    "signs and symptoms",
    "signs include",
    "common symptoms",
    "symptoms of",
    "symptom is",
    "symptoms:",
    "symptom:"
]


def normalize(text):

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    return re.sub(
        r"\s+",
        " ",
        text
    ).strip()


def contains_term(
    text,
    term
):

    text = normalize(text)
    term = normalize(term)

    return bool(
        re.search(
            r"(?<![a-z0-9])"
            + re.escape(term)
            + r"(?![a-z0-9])",
            text
        )
    )


def get_symptom_sections(
    summary
):

    text = normalize(summary)

    sections = []

    # Search for explicit symptom sections.
    for marker in SYMPTOM_SECTION_MARKERS:

        start = 0

        while True:

            index = text.find(
                marker,
                start
            )

            if index == -1:
                break

            # Capture a limited clinical context
            # after the symptom marker.
            section = text[
                index:
                index + 900
            ]

            sections.append(
                section
            )

            start = (
                index
                + len(marker)
            )

    return sections


def symptom_supported(
    symptom,
    title,
    summary
):

    title = normalize(title)

    sections = get_symptom_sections(
        summary
    )

    terms = SYMPTOM_TERMS.get(
        symptom,
        []
    )

    matched = []

    # A title match can be useful,
    # but only when the article also
    # has an explicit symptom section.
    for section in sections:

        for term in terms:

            if contains_term(
                section,
                term
            ):

                matched.append(
                    term
                )

    # If no symptom section exists,
    # don't infer clinical relevance
    # from arbitrary words in the article.
    if not sections:

        return []

    return list(
        dict.fromkeys(
            matched
        )
    )


def calculate_relevance(
    title,
    summary,
    symptoms
):

    matched_symptoms = []

    score = 0

    for symptom in symptoms:

        name = symptom.get(
            "symptom"
        )

        matched = symptom_supported(
            name,
            title,
            summary
        )

        if not matched:
            continue

        matched_symptoms.append(
            name
        )

        # Evidence only receives points
        # when the symptom is found inside
        # an explicit symptom/sign context.
        score += 3

    count = len(
        matched_symptoms
    )

    # Strong penalty for isolated matches.
    if count == 1:

        score = 0

    elif count == 2:

        score = 6

    elif count == 3:

        score = 9

    elif count >= 4:

        score = 12

    return score, matched_symptoms
