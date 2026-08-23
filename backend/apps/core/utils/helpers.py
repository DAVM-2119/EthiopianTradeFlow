import uuid
from datetime import datetime, timezone

def is_valid_uuid(val):
    """
    Validates if a given string or object is a valid UUID.
    """
    if isinstance(val, uuid.UUID):
        return True
    try:
        uuid.UUID(str(val))
        return True
    except (ValueError, TypeError, AttributeError):
        return False


def get_utc_now():
    """
    Returns current timezone-aware UTC datetime.
    """
    return datetime.now(timezone.utc)
