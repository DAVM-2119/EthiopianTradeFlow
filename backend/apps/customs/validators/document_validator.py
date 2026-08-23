import os
from typing import Tuple
from apps.core.exceptions import ValidationException

ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png'}
ALLOWED_MIME_TYPES = {'application/pdf', 'image/jpeg', 'image/png'}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit

def validate_uploaded_file(file_obj) -> Tuple[str, int, str]:
    """
    Validates uploaded file size, extension, and MIME type.
    """
    if not file_obj:
        raise ValidationException("File object is required.")

    size = getattr(file_obj, 'size', 0)
    if size <= 0 or size > MAX_FILE_SIZE_BYTES:
        raise ValidationException(f"File size must be greater than 0 and less than {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB.")

    orig_name = getattr(file_obj, 'name', 'file')
    ext = os.path.splitext(orig_name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationException(f"File extension '{ext}' is not permitted. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}.")

    content_type = getattr(file_obj, 'content_type', 'application/pdf')
    if content_type not in ALLOWED_MIME_TYPES and not content_type.startswith('application/') and not content_type.startswith('image/'):
        raise ValidationException(f"File MIME type '{content_type}' is invalid.")

    return orig_name, size, content_type
