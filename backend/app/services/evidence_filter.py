from app.services.condition_registry import (
    is_curated_condition,
    get_category
)


GENERIC_TOPICS = {
    "eye care",
    "caregiver health",
    "healthy aging",
    "medical tests",
    "health screening",
    "general health",
    "blood glucose"
}


def normalize_title(title):

    return title.lower().strip()


def filter_evidence(results):

    strong = []
    moderate = []

    for item in results:

        title = item.get(
            "title",
            ""
        )

        normalized = normalize_title(
            title
        )

        matched = item.get(
            "matched_symptoms",
            []
        )

        score = item.get(
            "relevance_score",
            0
        )

        count = len(
            matched
        )

        # Reject generic educational
        # pages from disease evidence.
        if normalized in GENERIC_TOPICS:
            continue

        # Only curated medical conditions
        # can appear in the condition section.
        if not is_curated_condition(title):
            continue

        # Minimum evidence threshold.
        if count < 3:
            continue

        item["condition_category"] = (
            get_category(title)
        )

        # Strong evidence.
        if count >= 3 and score >= 9:

            item[
                "evidence_level"
            ] = "strong"

            strong.append(item)

            continue

        # Moderate evidence.
        if count >= 3 and score >= 8:

            item[
                "evidence_level"
            ] = "moderate"

            moderate.append(item)

    strong.sort(
        key=lambda item: (
            len(
                item.get(
                    "matched_symptoms",
                    []
                )
            ),
            item.get(
                "relevance_score",
                0
            )
        ),
        reverse=True
    )

    moderate.sort(
        key=lambda item: (
            len(
                item.get(
                    "matched_symptoms",
                    []
                )
            ),
            item.get(
                "relevance_score",
                0
            )
        ),
        reverse=True
    )

    return (
        strong[:5],
        moderate[:3]
    )
