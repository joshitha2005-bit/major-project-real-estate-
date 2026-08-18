import os
import uuid
from fastapi import UploadFile

class StorageService:
    @staticmethod
    async def upload_property_image(file: UploadFile, property_id: int) -> str:
        """
        Saves the file locally in static/uploads/property_{property_id} and returns the relative URL.
        Designed as a clean storage abstraction.
        """
        # Resolve static dir path relative to this service file
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        static_dir = os.path.join(base_dir, "static")
        uploads_dir = os.path.join(static_dir, "uploads", f"property_{property_id}")
        os.makedirs(uploads_dir, exist_ok=True)

        # Generate unique file name
        ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{ext}"
        dest_path = os.path.join(uploads_dir, filename)

        # Read and write file
        content = await file.read()
        with open(dest_path, "wb") as f:
            f.write(content)

        # Return static served URL reference path
        return f"/static/uploads/property_{property_id}/{filename}"
