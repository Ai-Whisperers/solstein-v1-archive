"""Input validation and sanitization.

EPIC-027 Story 5: Prevent injection attacks.

Usage:
    from solstein.security.validation import sanitize_html, validate_file_upload

    clean = sanitize_html(user_input)
    validate_file_upload(file, allowed_extensions={'.pdf'})
"""

import re
from pathlib import Path
from typing import Any

from fastapi import HTTPException, UploadFile

# Allowed file extensions
ALLOWED_EXTENSIONS = {".pdf", ".xlsx", ".csv", ".json", ".md"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/csv",
    "application/json",
    "text/markdown",
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def sanitize_html(value: str | None) -> str:
    """Remove potentially dangerous HTML.

    Args:
        value: Input string.

    Returns:
        Sanitized string.
    """
    if not value:
        return ""

    try:
        import bleach

        return bleach.clean(value, tags=[], strip=True)
    except ImportError:
        # Fallback: remove HTML tags manually
        return re.sub(r"<[^>]+>", "", value)


def validate_sql_safe(value: str) -> str:
    """Validate string is safe from SQL injection.

    Args:
        value: Input string.

    Returns:
        Validated string.

    Raises:
        ValueError: If potentially dangerous characters found.
    """
    dangerous = [";", "--", "/*", "*/", "xp_", "sp_", "exec(", "select ", "drop ", "insert "]

    value_lower = value.lower()
    for pattern in dangerous:
        if pattern in value_lower:
            raise ValueError(f"Potentially dangerous SQL pattern detected: {pattern}")

    return value


def validate_file_upload(
    file: UploadFile,
    allowed_extensions: set[str] | None = None,
    max_size: int = MAX_FILE_SIZE,
) -> None:
    """Validate file upload.

    Args:
        file: Uploaded file.
        allowed_extensions: Set of allowed extensions.
        max_size: Maximum file size in bytes.

    Raises:
        HTTPException: If validation fails.
    """
    extensions = allowed_extensions or ALLOWED_EXTENSIONS

    # Check extension
    if file.filename:
        ext = Path(file.filename).suffix.lower()
        if ext not in extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {ext} not allowed. Allowed: {', '.join(extensions)}",
            )

    # Check size
    content = file.file.read()
    file.file.seek(0)  # Reset for later use

    if len(content) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {max_size / 1024 / 1024}MB",
        )


def validate_company_name(name: str) -> str:
    """Validate company name.

    Args:
        name: Company name.

    Returns:
        Validated name.

    Raises:
        ValueError: If invalid.
    """
    if not name or len(name.strip()) == 0:
        raise ValueError("Company name cannot be empty")

    if len(name) > 200:
        raise ValueError("Company name too long (max 200 characters)")

    # Check for injection attempts
    dangerous = ["<", ">", "{", "}", "$", ";", "--"]
    for char in dangerous:
        if char in name:
            raise ValueError(f"Invalid character in company name: {char}")

    return name.strip()


def validate_email(email: str) -> str:
    """Validate email address.

    Args:
        email: Email address.

    Returns:
        Validated email.

    Raises:
        ValueError: If invalid.
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        raise ValueError("Invalid email format")
    return email.lower()


def validate_url(url: str) -> str:
    """Validate URL.

    Args:
        url: URL string.

    Returns:
        Validated URL.

    Raises:
        ValueError: If invalid.
    """
    pattern = r"^https?://"
    if not re.match(pattern, url, re.IGNORECASE):
        raise ValueError("URL must start with http:// or https://")
    return url
