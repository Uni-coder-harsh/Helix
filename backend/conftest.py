from helix_platform.runtime import configure_asyncio_runtime
from helix_platform.telemetry import shutdown_telemetry

configure_asyncio_runtime()


def pytest_sessionfinish(session, exitstatus) -> None:  # type: ignore[no-untyped-def]
    del session, exitstatus
    shutdown_telemetry()
