import asyncio
import logging
import os
from typing import Any, cast

logger = logging.getLogger(__name__)


class PipeWakeupSelectorEventLoop(asyncio.SelectorEventLoop):
    """Selector loop variant that uses an OS pipe for cross-thread wakeups."""

    _self_read_fd: int | None
    _self_write_fd: int | None

    def _make_self_pipe(self) -> None:
        loop = cast(Any, self)
        self._self_read_fd, self._self_write_fd = os.pipe()
        os.set_blocking(self._self_read_fd, False)
        os.set_blocking(self._self_write_fd, False)
        loop._internal_fds += 1
        loop._add_reader(self._self_read_fd, self._read_from_self)

    def _read_from_self(self) -> None:
        loop = cast(Any, self)
        read_fd = self._self_read_fd
        if read_fd is None:
            return

        while True:
            try:
                data = os.read(read_fd, 4096)
                if not data:
                    break
                loop._process_self_data(data)
            except InterruptedError:
                continue
            except BlockingIOError:
                break

    def _write_to_self(self) -> None:
        loop = cast(Any, self)
        write_fd = getattr(self, "_self_write_fd", None)
        if write_fd is None:
            return

        try:
            os.write(write_fd, b"\0")
        except OSError:
            if loop._debug:
                logger.debug("failed_to_write_asyncio_wakeup_pipe", exc_info=True)

    def _close_self_pipe(self) -> None:
        loop = cast(Any, self)
        read_fd = getattr(self, "_self_read_fd", None)
        if read_fd is not None:
            loop._remove_reader(read_fd)
            os.close(read_fd)
            self._self_read_fd = None

        write_fd = getattr(self, "_self_write_fd", None)
        if write_fd is not None:
            os.close(write_fd)
            self._self_write_fd = None

        loop._internal_fds -= 1


class PipeWakeupEventLoopPolicy(asyncio.DefaultEventLoopPolicy):
    def new_event_loop(self) -> PipeWakeupSelectorEventLoop:
        return PipeWakeupSelectorEventLoop()


def configure_asyncio_runtime() -> None:
    """Install a wakeup policy that works when threaded socket sends are blocked."""
    current_policy = asyncio.get_event_loop_policy()
    if isinstance(current_policy, PipeWakeupEventLoopPolicy):
        return

    asyncio.set_event_loop_policy(PipeWakeupEventLoopPolicy())
