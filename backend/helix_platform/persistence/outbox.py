import datetime
import uuid

from sqlalchemy import Column, DateTime, String, Text

from helix_platform.persistence import Base


class OutboxEvent(Base):
    """Database model representing an Outbox Event for transaction-wrapped events."""

    __tablename__ = "outbox_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String(100), nullable=False)
    aggregate_type = Column(String(100), nullable=False)
    aggregate_id = Column(String(100), nullable=False)
    payload = Column(Text, nullable=False)  # JSON-serialized payload
    created_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )
    processed_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<OutboxEvent id={self.id} type={self.event_type} processed={self.processed_at is not None}>"
