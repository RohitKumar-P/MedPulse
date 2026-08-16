from app.knowledge.interpretation import build_interpretation


def _compact_source_summary(text, limit=500):

    if not text:
        return None

    text = " ".join(
        str(text).split()
    )

    if len(text) <= limit:
        return text

    return text[:limit].rsplit(
        " ",
        1
    )[0] + "..."


def _build_evidence_item(item):

    return {
        "medical_topic":
            item.get("title"),

        "plain_name":
            item.get(
                "plain_name",
                item.get("title")
            ),

        "category":
            item.get(
                "condition_category"
            ),

        "evidence_level":
            item.get(
                "evidence_level"
            ),

        "matched_symptoms":
            item.get(
                "matched_symptoms",
                []
            ),

        "match_count":
            len(
                item.get(
                    "matched_symptoms",
                    []
                )
            ),

        "evidence_type":
            item.get(
                "evidence_type",
                "condition"
            ),

        "clinical_confirmation_required":
            item.get(
                "requires_clinical_confirmation",
                True
            ),

        "cannot_distinguish_from":
            item.get(
                "cannot_distinguish",
                []
            ),

        "source":
            item.get(
                "source"
            ),

        "organization":
            item.get(
                "organization"
            ),

        "source_url":
            item.get(
                "url"
            ),

        "source_summary":
            _compact_source_summary(
                item.get(
                    "summary"
                )
            )
    }


def plain_language_report(
    assessment
):

    symptoms = assessment.get(
        "detected_symptoms",
        []
    )

    emergency = assessment.get(
        "emergency",
        {}
    )

    evidence = assessment.get(
        "evidence",
        {}
    )

    topics = evidence.get(
        "health_topics",
        []
    )

    interpretation = build_interpretation(
        topics
    )

    matches = interpretation[
        "evidence"
    ]

    if emergency.get(
        "status"
    ) == "urgent":

        summary = (
            "Some symptoms you reported "
            "match published warning signs. "
            "Please seek urgent medical attention."
        )

    elif matches:

        summary = (
            "Some of your symptoms overlap "
            "with information about specific "
            "medical conditions. This is not "
            "a diagnosis."
        )

    else:

        summary = (
            "Aegis did not find enough "
            "specific evidence for a "
            "meaningful condition match."
        )

    return {

        "title":
            "Your Aegis Health Summary",

        "language":
            "plain",

        "what_you_reported": [
            item["symptom"].replace(
                "_",
                " "
            )
            for item in symptoms
        ],

        "urgency":
            emergency.get(
                "status",
                "unknown"
            ),

        "summary":
            summary,

        "evidence_matches": [

            {
                "name":
                    item.get(
                        "plain_name",
                        item.get("title")
                    ),

                "evidence_level":
                    item.get(
                        "evidence_level"
                    ),

                "matched_symptoms":
                    item.get(
                        "matched_symptoms",
                        []
                    ),

                "source":
                    item.get(
                        "source"
                    ),

                "source_url":
                    item.get(
                        "url"
                    )
            }

            for item in matches
        ],

        "ambiguity":
            interpretation[
                "ambiguity"
            ],

        "important_note":
            (
                "Aegis identifies evidence "
                "matches. It does not diagnose "
                "disease from symptoms alone."
            )
    }


def detailed_report(
    assessment
):

    symptoms = assessment.get(
        "detected_symptoms",
        []
    )

    emergency = assessment.get(
        "emergency",
        {}
    )

    evidence = assessment.get(
        "evidence",
        {}
    )

    topics = evidence.get(
        "health_topics",
        []
    )

    interpretation = build_interpretation(
        topics
    )

    matches = interpretation[
        "evidence"
    ]

    return {

        "title":
            "Aegis Detailed Clinical Evidence Analysis",

        "language":
            "technical",

        "detected_symptoms":
            symptoms,

        "emergency_assessment":
            emergency,

        "evidence_matches": [
            _build_evidence_item(
                item
            )
            for item in matches
        ],

        "ambiguity":
            interpretation[
                "ambiguity"
            ],

        "clinical_status": {

            "diagnosis":
                "NOT ESTABLISHED",

            "differential_diagnosis":
                "NOT ESTABLISHED",

            "evidence_interpretation":
                (
                    "Symptoms were compared "
                    "against source-supported "
                    "clinical information."
                ),

            "clinical_confirmation":
                (
                    "Required where indicated "
                    "by the relevant clinical "
                    "evaluation."
                )
        },

        "safety_policy": {

            "diagnosis_from_symptoms":
                False,

            "automatic_medication":
                False,

            "automatic_treatment":
                False,

            "unsupported_claims":
                False,

            "source_required":
                True
        },

        "limitations": [

            "Symptom overlap does not establish a diagnosis.",

            "Different conditions can produce similar symptoms.",

            "Clinical history and examination may change interpretation.",

            "Diagnostic testing may be required.",

            "Aegis does not replace a healthcare professional."

        ]
    }
