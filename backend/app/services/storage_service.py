import os
import uuid
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile, HTTPException, status

ALLOWED_EXTENSIONS = {
    ".pdf", ".zip", ".docx", ".doc", ".txt", ".png", ".jpg", ".jpeg", ".csv", ".py", ".json", ".md"
}
DEFAULT_MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


class StorageService:
    """Safe local / object storage abstraction for assignment submissions."""

    def __init__(self, storage_dir: str = "storage/submissions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def validate_file(
        self,
        filename: str,
        file_size: int,
        allowed_types_str: str = "pdf,zip,docx,txt,png,jpg",
        max_size_mb: int = 10,
    ) -> None:
        """Validate filename extension and byte size."""
        if not filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename cannot be empty.",
            )

        _, ext = os.path.splitext(filename)
        ext = ext.lower()

        # Check against system allowed extensions and assignment specific extensions
        configured_allowed = {
            f".{t.strip().lower().lstrip('.')}"
            for t in allowed_types_str.split(",")
            if t.strip()
        }

        if ext not in configured_allowed or ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File extension '{ext}' is not permitted. Allowed: {allowed_types_str}",
            )

        max_bytes = max_size_mb * 1024 * 1024
        if file_size > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds the allowed limit of {max_size_mb} MB.",
            )

    async def save_upload(
        self,
        file: UploadFile,
        allowed_types_str: str = "pdf,zip,docx,txt,png,jpg",
        max_size_mb: int = 10,
    ) -> Tuple[str, str, int]:
        """
        Reads, validates, and saves an uploaded file safely to disk.
        Returns: (file_url, original_filename, file_size_bytes)
        """
        original_name = file.filename or "submission_file"
        _, ext = os.path.splitext(original_name)

        content = await file.read()
        file_size = len(content)

        self.validate_file(
            filename=original_name,
            file_size=file_size,
            allowed_types_str=allowed_types_str,
            max_size_mb=max_size_mb,
        )

        unique_name = f"{uuid.uuid4().hex}{ext.lower()}"
        target_path = self.storage_dir / unique_name

        with open(target_path, "wb") as f:
            f.write(content)

        file_url = f"/api/v1/assignments/submissions/files/{unique_name}"
        return file_url, original_name, file_size

    def get_file_path(self, unique_filename: str) -> Path:
        """Resolve safely to prevent path traversal attacks."""
        safe_name = os.path.basename(unique_filename)
        target = self.storage_dir / safe_name
        if not target.exists() or not target.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requested submission file was not found.",
            )
        return target


storage_service = StorageService()
