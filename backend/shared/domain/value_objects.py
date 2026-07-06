from dataclasses import dataclass

from shared.domain.base import ValidationException, ValueObject


@dataclass(frozen=True)
class Location(ValueObject):
    latitude: float
    longitude: float
    formatted_address: str

    def __post_init__(self) -> None:
        # Validate coordinates
        if not (-90.0 <= self.latitude <= 90.0):
            raise ValidationException(
                f"Latitude must be between -90 and 90. Got: {self.latitude}"
            )
        if not (-180.0 <= self.longitude <= 180.0):
            raise ValidationException(
                f"Longitude must be between -180 and 180. Got: {self.longitude}"
            )
        if not self.formatted_address or not self.formatted_address.strip():
            raise ValidationException("Formatted address cannot be empty.")


@dataclass(frozen=True)
class Attachment(ValueObject):
    file_url: str
    file_name: str
    mime_type: str
    file_size_bytes: int
    checksum: str

    def __post_init__(self) -> None:
        if not self.file_url or not self.file_url.strip():
            raise ValidationException("File URL cannot be empty.")
        if not self.file_name or not self.file_name.strip():
            raise ValidationException("File name cannot be empty.")
        if not self.mime_type or not self.mime_type.strip():
            raise ValidationException("MIME type cannot be empty.")
        if self.file_size_bytes <= 0:
            raise ValidationException(
                f"File size must be positive. Got: {self.file_size_bytes}"
            )
        if not self.checksum or not self.checksum.strip():
            raise ValidationException("Checksum cannot be empty.")
