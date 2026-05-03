from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils.cloudinary_config import upload_file
from app.modules.timeline import add_to_timeline

router = APIRouter()

@router.post("/{patient_id}")
async def upload(patient_id: str, file: UploadFile = File(...)):
    try:
        url = upload_file(file.file)

        add_to_timeline(
            patient_id=patient_id,
            event_type="file",
            data={"url": url}
        )

        return {"url": url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def upload_simple(file: UploadFile = File(...)):
    try:
        url = upload_file(file.file)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))