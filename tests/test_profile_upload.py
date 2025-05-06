import pytest
from httpx import AsyncClient
from pathlib import Path
from app.main import app # Import the FastAPI app

TEST_IMAGE_PATH = Path(__file__).parent / "test_image.jpg"

@pytest.mark.asyncio
async def test_upload_profile_picture():
    # Ensure the test image exists
    if not TEST_IMAGE_PATH.exists():
        with open(TEST_IMAGE_PATH, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n")  # PNG file header

    async with AsyncClient(app=app, base_url="http://test") as ac:
        with open(TEST_IMAGE_PATH, "rb") as image_file:
            response = await ac.post(
                "/profile/upload-picture",
                files={"file": ("test_image.jpg", image_file, "image/jpeg")},
            )
    
    print("\nResponse JSON:", response.json())
    print("Status Code:", response.status_code)
    print("Full Response:", response.text)

    assert response.status_code == 200
    data = response.json()
    assert "filename" in data
    assert "url" in data
    assert data["filename"].endswith(".jpg")
    assert data["url"].startswith("http://localhost:9000/profile-pics/")
