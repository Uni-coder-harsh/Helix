import re

from shared.domain.base import ValidationException

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def validate_non_empty_string(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValidationException(f"Field {field_name} must be a string.")
    cleaned = value.strip()
    if not cleaned:
        raise ValidationException(f"Field {field_name} cannot be empty or whitespace.")
    return cleaned


def validate_email(email: str) -> str:
    cleaned = validate_non_empty_string(email, "email")
    if not EMAIL_REGEX.match(cleaned):
        raise ValidationException(f"Invalid email address format: {email}")
    return cleaned


def validate_range(
    value: float, field_name: str, min_val: float, max_val: float
) -> float:
    if not (min_val <= value <= max_val):
        raise ValidationException(
            f"Field {field_name} must be between {min_val} and {max_val}. Got: {value}"
        )
    return value
