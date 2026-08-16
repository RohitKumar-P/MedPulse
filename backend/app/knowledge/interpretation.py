from app.knowledge.clinical_knowledge import (
    get_clinical_knowledge
)


def enrich_evidence(
    evidence
):

    enriched = []

    for item in evidence:

        title = item.get(
            "title"
        )

        knowledge = (
            get_clinical_knowledge(
                title
            )
        )

        result = dict(item)

        if knowledge:

            result[
                "plain_name"
            ] = knowledge[
                "plain_name"
            ]

            result[
                "condition_category"
            ] = knowledge[
                "category"
            ]

            result[
                "evidence_type"
            ] = knowledge[
                "evidence_type"
            ]

            result[
                "requires_clinical_confirmation"
            ] = knowledge[
                "requires_clinical_confirmation"
            ]

            result[
                "cannot_distinguish"
            ] = knowledge[
                "cannot_distinguish"
            ]

        else:

            result[
                "knowledge_status"
            ] = "not_yet_curated"

            result[
                "requires_clinical_confirmation"
            ] = True

        enriched.append(
            result
        )

    return enriched


def build_interpretation(
    evidence
):

    evidence = enrich_evidence(
        evidence
    )

    ambiguity = []

    seen = set()

    for item in evidence:

        for condition in item.get(
            "cannot_distinguish",
            []
        ):

            if condition in seen:
                continue

            seen.add(
                condition
            )

            ambiguity.append(
                condition
            )

    return {

        "evidence": evidence,

        "ambiguity": {

            "present":
                len(ambiguity) > 0,

            "conditions":
                ambiguity,

            "message":
                (
                    "Symptoms alone may not "
                    "distinguish between related "
                    "conditions. Clinical evaluation "
                    "and appropriate testing may "
                    "be required."
                )
        }
    }
