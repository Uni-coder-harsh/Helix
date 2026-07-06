import asyncio
import inspect
from collections.abc import Callable
from typing import Any, ClassVar

from helix_platform.logging import get_logger

logger = get_logger("event_bus")


class EventBus:
    """In-memory asynchronous Publish-Subscribe Event Bus for Helix microservices."""

    _handlers: ClassVar[dict[str, list[Callable[[Any], Any]]]] = {}
    _background_tasks: ClassVar[set[asyncio.Task[Any]]] = set()

    @classmethod
    def subscribe(cls, event_type: str | type, handler: Callable[[Any], Any]) -> None:
        """Register an event handler for a specific event type."""
        event_name = event_type if isinstance(event_type, str) else event_type.__name__
        if event_name not in cls._handlers:
            cls._handlers[event_name] = []
        cls._handlers[event_name].append(handler)
        logger.info("event_subscribed", event_type=event_name, handler=handler.__name__)

    @classmethod
    def publish(cls, event: Any) -> None:
        """Publishes an event asynchronously to all registered subscriber handlers."""
        event_name = type(event).__name__
        handlers = cls._handlers.get(event_name, [])
        if not handlers:
            logger.debug("no_subscribers_for_event", event_type=event_name)
            return

        logger.info(
            "publishing_event",
            event_type=event_name,
            subscribers_count=len(handlers),
        )
        for handler in handlers:
            # Run concurrently in the background and keep a strong reference
            task = asyncio.create_task(cls._execute_handler(handler, event))
            cls._background_tasks.add(task)
            task.add_done_callback(cls._background_tasks.discard)

    @classmethod
    async def _execute_handler(cls, handler: Callable[[Any], Any], event: Any) -> None:
        """Executes a handler, supporting both async and sync execution signatures."""
        try:
            if inspect.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        except Exception as e:
            logger.error(
                "event_handler_failed",
                event_type=type(event).__name__,
                handler=handler.__name__,
                error=str(e),
                exc_info=True,
            )
