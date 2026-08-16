from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Depends
)

import os
import shutil
import tempfile

from app.api.auth import require_roles

from app.records.record_engine import (
    process_record
)

from app.records.timeline import (
    build_timeline,
    compare_laboratory_values
)


router = APIRouter(
    prefix="/records",
    tags=["Medical Records"]
)


@router.post("/upload")
async def upload_record(
    file: UploadFile = File(...),
    current_user=Depends(require_roles("admin", "doctor", "staff"))
):

    allowed = {
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
        ".webp"
    }

    extension = os.path.splitext(
        file.filename
    )[1].lower()

    if extension not in allowed:

        raise HTTPException(
            status_code=400,
            detail=(
                "Supported formats: "
                "PDF, PNG, JPG, JPEG, WEBP"
            )
        )

    temporary = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=extension
    )

    try:

        with temporary as output:

            shutil.copyfileobj(
                file.file,
                output
            )

        record = process_record(
            temporary.name,
            file.filename
        )

        return {
            "status": "success",
            "record": record
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:

        try:
            os.unlink(
                temporary.name
            )
        except Exception:
            pass


@router.get("/timeline")
def medical_timeline(current_user=Depends(require_roles("admin", "doctor", "staff"))):

    return {
        "status": "success",
        "timeline":
            build_timeline()
    }


@router.get("/laboratory-trends")
def laboratory_trends(current_user=Depends(require_roles("admin", "doctor", "staff"))):

    return {
        "status": "success",
        "values":
            compare_laboratory_values()
    }
