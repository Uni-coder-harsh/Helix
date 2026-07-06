import uuid
from abc import ABC, abstractmethod


class NotificationRepository(ABC):
    """Domain interface for sending system notifications."""

    @abstractmethod
    def notify(self, citizen_id: uuid.UUID, message: str) -> None:
        """Sends an operational SMS/notification to a citizen."""
        pass
