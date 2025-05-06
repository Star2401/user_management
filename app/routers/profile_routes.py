from fastapi import APIRouter, File, UploadFile, HTTPException
from minio import Minio
import uuid
import io

router = APIRouter(prefix="/profile", tags=["Profile"])

# Initialize Minio client
minio_client = Minio(
    "minio:9000",
    access_key="minioadmin",
    secret_key="minioadmin123",
    secure=False
)

@router.post("/upload-picture")
async def upload_profile_picture(file: UploadFile = File(...)):
    try:
        file_ext = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        content = await file.read()
        file_stream = io.BytesIO(content)

        minio_client.put_object(
            "profile-pics",
            unique_filename,
            data=file_stream,
            length=len(content),
            content_type=file.content_type,
        )

        return {
            "filename": unique_filename,
            "url": f"http://localhost:9000/profile-pics/{unique_filename}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
