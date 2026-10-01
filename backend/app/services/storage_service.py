import os
import io
import uuid
from fastapi import UploadFile, HTTPException
from PIL import Image

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}

class StorageService:
    @staticmethod
    async def upload_property_image(file: UploadFile, property_id: int) -> str:
        """
        Validates file size, extension, MIME type, and actual image binary structure (via PIL),
        then saves the file locally under static/uploads/property_{property_id}/.
        """
        # 1. Sanitize filename & extract extension (prevent path traversal)
        raw_filename = os.path.basename(file.filename or "")
        ext = os.path.splitext(raw_filename)[1].lower()
        
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file extension '{ext}'. Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )

        # 2. Check Content-Type header
        content_type = (file.content_type or "").lower()
        if content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid MIME type '{content_type}'. Allowed MIME types: {', '.join(sorted(ALLOWED_MIME_TYPES))}"
            )

        # 3. Read content and enforce size limit
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"File size exceeds maximum allowed limit of 5 MB.")

        # 4. Verify actual binary content using PIL (rejects renamed executables or corrupted files)
        try:
            img = Image.open(io.BytesIO(content))
            img.verify()
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="File content validation failed. Uploaded file is not a valid image or is corrupted."
            )

        # 5. Resolve destination directory and safe random UUID filename
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        uploads_dir = os.path.join(base_dir, "static", "uploads", f"property_{property_id}")
        os.makedirs(uploads_dir, exist_ok=True)

        safe_filename = f"{uuid.uuid4().hex}{ext}"
        dest_path = os.path.join(uploads_dir, safe_filename)

        # 6. Write file binary to disk
        with open(dest_path, "wb") as f:
            f.write(content)

        return f"/static/uploads/property_{property_id}/{safe_filename}"

    @staticmethod
    def delete_property_image_file(image_path: str) -> bool:
        """Safely delete uploaded property image file from disk if it exists."""
        if not image_path or not image_path.startswith("/static/uploads/"):
            return False
            
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # Strip leading slash
        clean_rel = image_path.lstrip("/").replace("/", os.sep)
        full_path = os.path.abspath(os.path.join(base_dir, clean_rel))

        # Prevent path traversal outside static/uploads
        allowed_prefix = os.path.abspath(os.path.join(base_dir, "static", "uploads"))
        if not full_path.startswith(allowed_prefix):
            return False

        if os.path.exists(full_path) and os.path.isfile(full_path):
            try:
                os.remove(full_path)
                return True
            except Exception as e:
                print(f"Error removing file {full_path}: {e}")
                return False
        return False

