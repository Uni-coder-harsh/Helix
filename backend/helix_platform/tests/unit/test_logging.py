import uuid

from helix_platform.logging import correlation_id_var, request_id_var


def test_correlation_ids_in_contextvars() -> None:
    """Verifies that contextvars store ID values correctly and can be retrieved."""
    req_id = str(uuid.uuid4())
    corr_id = str(uuid.uuid4())

    request_id_var.set(req_id)
    correlation_id_var.set(corr_id)

    assert request_id_var.get() == req_id
    assert correlation_id_var.get() == corr_id
