import uuid
from abc import ABC
from datetime import UTC, datetime
from typing import Any


class DomainException(Exception):
    """Base exception for all domain-related errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ValidationException(DomainException):
    """Exception thrown when domain validation rules are violated."""

    pass


class InvalidStateTransitionException(DomainException):
    """Exception thrown when an invalid state transition is attempted on an entity."""

    pass


class DomainEvent(ABC):
    """Abstract base class for all Domain Events."""

    def __init__(
        self, event_id: uuid.UUID | None = None, occurred_on: datetime | None = None
    ) -> None:
        self.event_id: uuid.UUID = event_id or uuid.uuid4()
        self.occurred_on: datetime = occurred_on or datetime.now(UTC)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, DomainEvent):
            return False
        return self.event_id == other.event_id

    def __hash__(self) -> int:
        return hash(self.event_id)


class BaseEntity[TId](ABC):
    """Base class for all Domain Entities."""

    def __init__(self, id: TId) -> None:
        if id is None:
            raise ValidationException("Entity ID cannot be None.")
        self._id: TId = id

    @property
    def id(self) -> TId:
        return self._id

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, BaseEntity):
            return False
        if type(self) is not type(other):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash((type(self), self.id))


class AggregateRoot[TId](BaseEntity[TId], ABC):
    """Base class for all Aggregate Roots, which manage domain events."""

    def __init__(self, id: TId) -> None:
        super().__init__(id)
        self._domain_events: list[DomainEvent] = []

    @property
    def domain_events(self) -> list[DomainEvent]:
        """Get the read-only list of domain events."""
        return list(self._domain_events)

    def record_event(self, event: DomainEvent) -> None:
        """Record a new domain event."""
        self._domain_events.append(event)

    def clear_domain_events(self) -> None:
        """Clear all recorded domain events."""
        self._domain_events.clear()


class ValueObject(ABC):
    """Base class for all Value Objects.

    Value objects are compared by their attributes.
    """

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ValueObject):
            return False
        if type(self) is not type(other):
            return False
        return self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        # Simple hash based on attributes
        values = tuple(sorted((k, v) for k, v in self.__dict__.items()))
        return hash((type(self), values))
