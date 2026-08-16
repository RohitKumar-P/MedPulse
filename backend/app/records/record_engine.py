import os
import re
import uuid
import json
from datetime import datetime

import fitz
from PIL import Image
import pytesseract


RECORD_DIR = "data/medical_records"

os.makedirs(
    RECORD_DIR,
    exist_ok=True
)


def extract_pdf_text(path):

    document = fitz.open(path)

    pages = []

    for index, page in enumerate(document):

        pages.append({
            "page": index + 1,
            "text": page.get_text(
                "text"
            ).strip()
        })

    document.close()

    return pages


def extract_image_text(path):

    image = Image.open(path)

    return [{
        "page": 1,
        "text": pytesseract.image_to_string(
            image
        ).strip()
    }]


def extract_plain_text(path):

    with open(
        path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:

        text = file.read()

    return [{
        "page": 1,
        "text": text
    }]


def extract_text(
    path,
    filename
):

    extension = os.path.splitext(
        filename
    )[1].lower()

    if extension == ".pdf":
        return extract_pdf_text(path)

    if extension in (
        ".png",
        ".jpg",
        ".jpeg",
        ".webp"
    ):
        return extract_image_text(path)

    if extension in (
        ".txt",
        ".csv"
    ):
        return extract_plain_text(path)

    raise ValueError(
        "Unsupported medical record format"
    )


def normalize_text(text):

    return re.sub(
        r"\s+",
        " ",
        text
    ).strip()


def extract_dates(text):

    patterns = [

        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",

        r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b"
    ]

    results = []

    for pattern in patterns:

        results.extend(
            re.findall(
                pattern,
                text
            )
        )

    return list(
        dict.fromkeys(results)
    )


def extract_lab_values(text):

    pattern = re.compile(
        r"""
        (?P<name>
            blood\s+glucose|
            fasting\s+glucose|
            random\s+glucose|
            glucose|
            hba1c|
            hemoglobin\s+a1c|
            cholesterol|
            total\s+cholesterol|
            ldl|
            hdl|
            triglycerides|
            creatinine|
            hemoglobin|
            wbc|
            platelet|
            blood\s+pressure
        )
        \s*
        (?::|=|-)?\s*
        (?P<value>
            \d+(?:\.\d+)?
            (?:\s*/\s*\d+(?:\.\d+)?)?
        )
        \s*
        (?P<unit>
            mg/dL|
            mmol/L|
            g/dL|
            mmHg|
            %|
            cells/uL
        )?
        """,
        re.IGNORECASE |
        re.VERBOSE
    )

    results = []

    for match in pattern.finditer(text):

        results.append({

            "test":
                match.group("name").strip(),

            "value":
                match.group("value").strip(),

            "unit":
                match.group("unit"),

            "source_text":
                match.group(0),

            "evidence": {
                "type":
                    "extracted_from_record",
                "inferred":
                    False
            }
        })

    return results


def extract_medications(text):

    patterns = [

        r"\b(?:tablet|tab|capsule|cap)"
        r"\s+[A-Za-z][A-Za-z0-9-]+",

        r"\b[A-Z][A-Za-z-]{3,}"
        r"\s+\d+(?:\.\d+)?\s*mg\b"
    ]

    medications = []

    for pattern in patterns:

        medications.extend(
            re.findall(
                pattern,
                text,
                re.IGNORECASE
            )
        )

    return list(
        dict.fromkeys(
            medications
        ))


def extract_stated_diagnoses(text):

    patterns = [

        r"(?:diagnosis|diagnosed with)"
        r"\s*[:\-]?\s*([^\n.;]+)",

        r"(?:clinical impression)"
        r"\s*[:\-]?\s*([^\n.;]+)"
    ]

    diagnoses = []

    for pattern in patterns:

        diagnoses.extend(
            re.findall(
                pattern,
                text,
                re.IGNORECASE
            )
        )

    return list(
        dict.fromkeys(
            item.strip()
            for item in diagnoses
            if item.strip()
        ))


def parse_record(
    record_id,
    filename,
    pages
):

    full_text = "\n".join(
        page["text"]
        for page in pages
    )

    normalized = normalize_text(
        full_text
    )

    return {

        "record_id":
            record_id,

        "filename":
            filename,

        "processed_at":
            datetime.utcnow().isoformat(),

        "pages":
            pages,

        "dates":
            extract_dates(
                normalized
            ),

        "laboratory_values":
            extract_lab_values(
                normalized
            ),

        "medications":
            extract_medications(
                normalized
            ),

        "stated_diagnoses":
            extract_stated_diagnoses(
                normalized
            ),

        "extraction_policy": {

            "diagnosis_inference":
                False,

            "lab_interpretation":
                False,

            "medication_recommendation":
                False,

            "source_preserved":
                True,

            "record_statement_is_not_ai_diagnosis":
                True
        }
    }


def save_record(record):

    path = os.path.join(
        RECORD_DIR,
        f"{record['record_id']}.json"
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            record,
            file,
            indent=2,
            ensure_ascii=False
        )

    return path


def process_record(
    path,
    filename
):

    record_id = str(
        uuid.uuid4()
    )

    pages = extract_text(
        path,
        filename
    )

    record = parse_record(
        record_id,
        filename,
        pages
    )

    save_record(
        record
    )

    return record
