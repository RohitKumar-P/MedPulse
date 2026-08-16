import glob
import json
import os
from datetime import datetime


RECORD_DIR = "data/medical_records"


def load_records():

    records = []

    for path in glob.glob(
        os.path.join(
            RECORD_DIR,
            "*.json"
        )
    ):

        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            base_patient_id = data.get("patient_id")
            base_created_at = data.get("created_at")
            base_conditions = data.get("conditions", [])
            base_medications = data.get("medications", [])
            base_laboratory_results = data.get(
                "laboratory_results",
                []
            )
            base_allergies = data.get("allergies", [])

            nested_records = data.get("records", [])

            if nested_records:

                for item in nested_records:

                    records.append({
                        "patient_id":
                            base_patient_id,

                        "record_id":
                            item.get(
                                "record_id",
                                item.get("id", "")
                            ),

                        "filename":
                            os.path.basename(path),

                        "created_at":
                            base_created_at,

                        "processed_at":
                            item.get(
                                "added_at",
                                base_created_at
                            ),

                        "record_type":
                            item.get(
                                "record_type",
                                "unknown"
                            ),

                        "title":
                            item.get(
                                "title",
                                ""
                            ),

                        "content":
                            item.get(
                                "content",
                                ""
                            ),

                        "dates":
                            item.get(
                                "dates",
                                []
                            ),

                        "laboratory_values":
                            item.get(
                                "laboratory_values",
                                base_laboratory_results
                            ),

                        "medications":
                            item.get(
                                "medications",
                                base_medications
                            ),

                        "stated_diagnoses":
                            item.get(
                                "stated_diagnoses",
                                base_conditions
                            ),

                        "allergies":
                            item.get(
                                "allergies",
                                base_allergies
                            )
                    })

            else:

                records.append({
                    "patient_id":
                        base_patient_id,

                    "record_id":
                        data.get(
                            "record_id",
                            data.get("id", "")
                        ),

                    "filename":
                        os.path.basename(path),

                    "created_at":
                        base_created_at,

                    "processed_at":
                        data.get(
                            "processed_at",
                            base_created_at
                        ),

                    "record_type":
                        data.get(
                            "record_type",
                            "unknown"
                        ),

                    "title":
                        data.get(
                            "title",
                            ""
                        ),

                    "content":
                        data.get(
                            "content",
                            ""
                        ),

                    "dates":
                        data.get(
                            "dates",
                            []
                        ),

                    "laboratory_values":
                        data.get(
                            "laboratory_values",
                            base_laboratory_results
                        ),

                    "medications":
                        data.get(
                            "medications",
                            base_medications
                        ),

                    "stated_diagnoses":
                        data.get(
                            "stated_diagnoses",
                            base_conditions
                        ),

                    "allergies":
                        data.get(
                            "allergies",
                            base_allergies
                        )
                })

        except Exception:
            continue

    records.sort(
        key=lambda item:
            item.get(
                "processed_at",
                ""
            )
    )

    return records


def build_timeline():

    records = load_records()

    timeline = []

    for record in records:

        timeline.append({

            "record_id":
                record.get("record_id", record.get("id", "")),

            "filename":
                record.get("filename", ""),

            "dates":
                record.get(
                    "dates",
                    []
                ),

            "laboratory_values":
                record.get(
                    "laboratory_values",
                    []
                ),

            "medications":
                record.get(
                    "medications",
                    []
                ),

            "stated_diagnoses":
                record.get(
                    "stated_diagnoses",
                    []
                )
        })

    return timeline


def compare_laboratory_values():

    records = load_records()

    values = []

    for record in records:

        for result in record.get(
            "laboratory_values",
            []
        ):

            values.append({

                "record_id":
                    record["record_id"],

                "filename":
                    record["filename"],

                **result
            })

    return values
