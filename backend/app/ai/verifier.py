import re

from app.ai.schemas import MedicalExtraction
from app.ai.symptom_normalizer import (
    canonicalize_extraction
)


CONFIDENCE_MAP = {
    "very_low": 0.20,
    "low": 0.40,
    "medium": 0.65,
    "moderate": 0.65,
    "high": 0.85,
    "very_high": 0.95
}


PAST_TIME_PATTERNS = [
    r"\blast week\b",
    r"\blast month\b",
    r"\blast year\b",
    r"\byesterday\b",
    r"\bpreviously\b",
    r"\bprevious week\b",
    r"\bprevious month\b",
    r"\ba few days ago\b",
    r"\bdays ago\b",
    r"\bweeks ago\b",
    r"\bmonths ago\b",
    r"\byears ago\b",
    r"\bin the past\b",
    r"\bused to\b",
    r"\bhad .* but\b"
]


CURRENT_NEGATION_PATTERNS = [
    r"\bdon't have\b",
    r"\bdo not have\b",
    r"\bdoesn't have\b",
    r"\bdoes not have\b",
    r"\bno longer have\b",
    r"\bnot having\b",
    r"\bnot now\b",
    r"\bnot anymore\b",
    r"\bcurrently do not\b",
    r"\bcurrently don't\b"
]


def normalize_confidence(value):

    if isinstance(
        value,
        (int, float)
    ):

        return max(
            0.0,
            min(
                1.0,
                float(value)
            )
        )

    if isinstance(
        value,
        str
    ):

        value = (
            value
            .strip()
            .lower()
            .replace(
                " ",
                "_"
            )
        )

        if value in CONFIDENCE_MAP:

            return CONFIDENCE_MAP[
                value
            ]

        try:

            return max(
                0.0,
                min(
                    1.0,
                    float(value)
                )
            )

        except ValueError:

            return 0.0

    return 0.0


def normalize_symptom(
    symptom
):

    if not isinstance(
        symptom,
        dict
    ):

        return None

    name = (
        symptom.get("name")
        or symptom.get("symptom")
        or symptom.get("label")
    )

    if not name:

        return None

    return {

        "name":
            str(name).strip(),

        "confidence":
            normalize_confidence(
                symptom.get(
                    "confidence",
                    0
                )
            ),

        "severity":
            "unknown",

        "onset":
            symptom.get(
                "onset"
            ) or symptom.get(
                "time"
            ),

        "duration":
            symptom.get(
                "duration"
            ),

        "current":
            symptom.get(
                "current"
            ),

        "negated":
            bool(
                symptom.get(
                    "negated",
                    False
                )
            )
    }


def apply_temporal_safety(
    text,
    symptoms
):

    normalized_text = (
        str(text or "")
        .lower()
    )

    result = []

    for symptom in symptoms:

        name = symptom["name"]

        escaped = re.escape(
            name.replace(
                "_",
                " "
            )
        )

        symptom_position = (
            normalized_text.find(
                name.replace(
                    "_",
                    " "
                )
            )
        )

        if symptom_position == -1:

            # Keep AI extraction if the exact
            # canonical name isn't present.
            result.append(symptom)
            continue

        context_start = max(
            0,
            symptom_position - 100
        )

        context_end = min(
            len(normalized_text),
            symptom_position + 100
        )

        context = normalized_text[
            context_start:context_end
        ]

        past = any(
            re.search(
                pattern,
                context
            )
            for pattern
            in PAST_TIME_PATTERNS
        )

        current_denial = any(
            re.search(
                pattern,
                context
            )
            for pattern
            in CURRENT_NEGATION_PATTERNS
        )

        if (
            past
            and current_denial
        ):

            symptom["current"] = False
            symptom["negated"] = True

        elif past:

            symptom["current"] = False

        result.append(
            symptom
        )

    return result


def normalize_ai_output(
    data,
    source_text=""
):

    if not isinstance(
        data,
        dict
    ):

        raise ValueError(
            "AI output must be an object"
        )

    symptoms = []

    for item in data.get(
        "symptoms",
        []
    ):

        normalized = normalize_symptom(
            item
        )

        if normalized:

            symptoms.append(
                normalized
            )

    symptoms = apply_temporal_safety(
        source_text,
        symptoms
    )

    result = {

        "symptoms":
            symptoms,

        "medications":
            data.get(
                "medications",
                []
            ),

        "diagnoses":
            data.get(
                "diagnoses",
                []
            ),

        "allergies":
            data.get(
                "allergies",
                []
            ),

        "laboratory_results":
            data.get(
                "laboratory_results",
                []
            ),

        "missing_information":
            data.get(
                "missing_information",
                []
            ),

        "uncertainty":
            data.get(
                "uncertainty",
                []
            )
    }

    return canonicalize_extraction(
        result
    )


def validate_extraction(
    data,
    source_text=""
):

    normalized = normalize_ai_output(
        data,
        source_text
    )

    validated = (
        MedicalExtraction.model_validate(
            normalized
        )
    )

    validated.symptoms = [

        symptom

        for symptom
        in validated.symptoms

        if (
            not symptom.negated
            and symptom.confidence >= 0.60
        )
    ]

    return validated


def compare_extractions(
    primary,
    secondary
):

    primary_names = {
        x.name.lower()
        for x in primary.symptoms
    }

    secondary_names = {
        x.name.lower()
        for x in secondary.symptoms
    }

    return {

        "agreement":
            sorted(
                primary_names
                & secondary_names
            ),

        "disagreement":
            sorted(
                primary_names
                ^ secondary_names
            )
    }
