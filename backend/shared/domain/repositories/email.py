from abc import ABC, abstractmethod


class EmailRepository(ABC):
    """Domain interface for sending system email notifications."""

    @abstractmethod
    def send_email(
        self, to_email: str, subject: str, message: str, is_html: bool = False
    ) -> None:
        """Sends an email notification."""
        pass
