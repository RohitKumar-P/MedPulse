from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[3] / "knowledge"


def retrieve_evidence(disease: str, query: str = "") -> list[str]:
    """
    Lightweight local RAG retrieval.
    Reads relevant local knowledge files instead of allowing the LLM
    to invent medical information.
    """

    if not KNOWLEDGE_DIR.exists():
        return []

    terms = set(
        (disease + " " + query)
        .lower()
        .replace(",", " ")
        .split()
    )

    results = []

    for file in KNOWLEDGE_DIR.rglob("*"):
        if not file.is_file():
            continue

        if file.suffix.lower() not in {
            ".txt", ".md", ".json", ".csv"
        }:
            continue

        try:
            text = file.read_text(
                encoding="utf-8",
                errors="ignore"
            )
        except Exception:
            continue

        lower = text.lower()

        if disease.lower() in lower:
            results.append(
                f"Source: {file.name}\n{text[:4000]}"
            )

    return results[:5]
