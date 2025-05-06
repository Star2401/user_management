from fastapi import APIRouter, File, UploadFile, HTTPException
from minio import Minio
import uuid
import io
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter(prefix="/profile", tags=["Profile"])

# Initialize Minio client with env vars
minio_client = Minio(
    os.getenv("MINIO_ENDPOINT", "minio:9000"),
    access_key=os.getenv("MINIO_ROOT_USER", "minioadmin"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD", "minioadmin123"),
    secure=False
)

bucket_name = os.getenv("MINIO_BUCKET", "profile-pics")

@router.post("/upload-picture")
async def upload_profile_picture(file: UploadFile = File(...)):
    try:
        file_ext = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        content = await file.read()
        file_stream = io.BytesIO(content)

        # Upload to Minio
        minio_client.put_object(
            bucket_name,
            unique_filename,
            data=file_stream,
            length=len(content),
            content_type=file.content_type,
        )

        return {
            "filename": unique_filename,
            "url": f"http://localhost:9000/{bucket_name}/{unique_filename}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
