import json
import os
import uuid

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

RECORD_DIR = os.path.join(
    BASE_DIR,
    "storage",
    "records"
)

os.makedirs(
    RECORD_DIR,
    exist_ok=True
)


def save_record(record):

    record_id = str(uuid.uuid4())

    path = os.path.join(
        RECORD_DIR,
        f"{record_id}.json"
    )

    data = {
        "id": record_id,
        **record
    }

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )

    return data


def list_records():

    records = []

    for filename in os.listdir(RECORD_DIR):

        if not filename.endswith(".json"):
            continue

        path = os.path.join(
            RECORD_DIR,
            filename
        )

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            records.append(
                json.load(file)
            )

    records.sort(
        key=lambda x: x.get(
            "record_date",
            ""
        ),
        reverse=True
    )

    return records
