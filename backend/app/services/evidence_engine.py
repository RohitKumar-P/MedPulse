import re
import httpx
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

from app.services.evidence_relevance import calculate_relevance
from app.services.evidence_filter import filter_evidence


MEDLINEPLUS_URL = "https://wsearch.nlm.nih.gov/ws/query"

PUBMED_SEARCH_URL = (
    "https://eutils.ncbi.nlm.nih.gov/"
    "entrez/eutils/esearch.fcgi"
)

PUBMED_SUMMARY_URL = (
    "https://eutils.ncbi.nlm.nih.gov/"
    "entrez/eutils/esummary.fcgi"
)

CLINICAL_TRIALS_URL = (
    "https://clinicaltrials.gov/api/v2/studies"
)


def clean_text(value):

    if not value:
        return ""

    return re.sub(
        r"\s+",
        " ",
        BeautifulSoup(
            value,
            "html.parser"
        ).get_text(
            " ",
            strip=True
        )
    ).strip()


async def search_medlineplus(
    query,
    limit=8
):

    params = {
        "db": "healthTopics",
        "term": query,
        "retmax": limit,
        "rettype": "brief",
        "tool": "aegis_health_ai"
    }

    async with httpx.AsyncClient(timeout=20, follow_redirects=True, trust_env=False) as client:

        response = await client.get(
            MEDLINEPLUS_URL,
            params=params,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/151.0.0.0 Safari/537.36", "Accept": "application/json", "Referer": "https://clinicaltrials.gov/"}
        )

        response.raise_for_status()

    root = ET.fromstring(
        response.text
    )

    results = []

    for document in root.findall(
        ".//document"
    ):

        title = ""
        summary = ""

        for content in document.findall(
            "content"
        ):

            name = content.attrib.get(
                "name",
                ""
            )

            text = clean_text(
                "".join(
                    content.itertext()
                )
            )

            if name.lower() == "title":
                title = text

            elif name.lower() in (
                "fullsummary",
                "summary",
                "snippet"
            ) and not summary:

                summary = text

        if not title:
            continue

        results.append({

            "title": title,

            "summary": summary,

            "url":
                document.attrib.get(
                    "url"
                ),

            "source":
                "MedlinePlus",

            "organization":
                "U.S. National Library of Medicine"
        })

    return results


async def search_medlineplus_symptoms(
    symptoms
):

    candidates = []
    seen = set()

    for item in symptoms:

        phrases = item.get(
            "matched_phrases",
            []
        )

        query = (
            phrases[0]
            if phrases
            else item["symptom"].replace(
                "_",
                " "
            )
        )

        try:

            results = (
                await search_medlineplus(
                    query
                )
            )

        except Exception:

            continue

        for result in results:

            url = result.get(
                "url"
            )

            if not url or url in seen:
                continue

            seen.add(url)

            score, matched = (
                calculate_relevance(
                    result["title"],
                    result["summary"],
                    symptoms
                )
            )

            result["relevance_score"] = score

            result["matched_symptoms"] = (
                matched
            )

            candidates.append(
                result
            )

    candidates.sort(
        key=lambda item:
            item["relevance_score"],
        reverse=True
    )

    relevant = [

        item

        for item in candidates

        if item["relevance_score"] >= 2
    ]

    strong, moderate = (
        filter_evidence(
            relevant
        )
    )

    return strong + moderate


async def search_pubmed(
    query,
    limit=5
):

    params = {

        "db":
            "pubmed",

        "term":
            query,

        "retmax":
            limit,

        "retmode":
            "json",

        "sort":
            "relevance",

        "tool":
            "aegis_health_ai"
    }

    async with httpx.AsyncClient(timeout=20, follow_redirects=True, trust_env=False) as client:

        response = await client.get(
            PUBMED_SEARCH_URL,
            params=params,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/151.0.0.0 Safari/537.36", "Accept": "application/json", "Referer": "https://clinicaltrials.gov/"}
        )

        response.raise_for_status()

        data = response.json()

    ids = (
        data
        .get("esearchresult", {})
        .get("idlist", [])
    )

    if not ids:
        return []

    params = {

        "db":
            "pubmed",

        "id":
            ",".join(ids),

        "retmode":
            "json",

        "tool":
            "aegis_health_ai"
    }

    async with httpx.AsyncClient(timeout=20, follow_redirects=True, trust_env=False) as client:

        response = await client.get(
            PUBMED_SUMMARY_URL,
            params=params,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/151.0.0.0 Safari/537.36", "Accept": "application/json", "Referer": "https://clinicaltrials.gov/"}
        )

        response.raise_for_status()

        data = response.json()

    result_data = data.get(
        "result",
        {}
    )

    results = []

    for pmid in ids:

        record = result_data.get(
            pmid,
            {}
        )

        if not record:
            continue

        results.append({

            "pmid":
                pmid,

            "title":
                record.get(
                    "title",
                    "PubMed article"
                ),

            "url":
                f"https://pubmed.ncbi.nlm.nih.gov/"
                f"{pmid}/",

            "source":
                "PubMed",

            "organization":
                "U.S. National Library of Medicine"
        })

    return results


async def search_clinical_trials(
    condition,
    limit=5
):

    params = {

        "query.cond":
            condition,

        "pageSize":
            min(
                max(limit, 1),
                20
            ),

        "format":
            "json"
    }

    try:

        async with httpx.AsyncClient(timeout=20, follow_redirects=True, trust_env=False) as client:

            response = await client.get(
                CLINICAL_TRIALS_URL,
                params=params,
                headers={
                    "User-Agent": "Mozilla/5.0",

                    "Accept": "application/json", "Referer": "https://clinicaltrials.gov/"
                }
            )

            response.raise_for_status()

            data = response.json()

    except Exception as error:

        return {

            "available":
                False,

            "error":
                str(error),

            "studies":
                []
        }

    studies = []

    for study in data.get(
        "studies",
        []
    ):

        protocol = study.get(
            "protocolSection",
            {}
        )

        identification = (
            protocol.get(
                "identificationModule",
                {}
            )
        )

        status = (
            protocol.get(
                "statusModule",
                {}
            )
        )

        nct_id = identification.get(
            "nctId"
        )

        title = identification.get(
            "briefTitle"
        )

        if not nct_id or not title:
            continue

        studies.append({

            "nct_id":
                nct_id,

            "title":
                title,

            "status":
                status.get(
                    "overallStatus"
                ),

            "url":
                f"https://clinicaltrials.gov/study/"
                f"{nct_id}",

            "source":
                "ClinicalTrials.gov",

            "note":
                "Research discovery only. "
                "Verify eligibility using "
                "the official study record."
        })

    return {

        "available":
            True,

        "error":
            None,

        "studies":
            studies
    }


async def build_evidence(
    symptoms,
    raw_text
):

    health_topics = (
        await search_medlineplus_symptoms(
            symptoms
        )
    )

    research = []

    try:

        research = await search_pubmed(
            raw_text,
            limit=5
        )

    except Exception:

        research = []

    return {

        "health_topics":
            health_topics,

        "research":
            research,

        "evidence_policy": {

            "diagnosis":
                False,

            "treatment_recommendation":
                False,

            "symptom_based_conclusion":
                False,

            "source_required":
                True,

            "primary_sources": [
                "MedlinePlus",
                "PubMed"
            ]
        }
    }



