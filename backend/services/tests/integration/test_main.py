from fastapi.testclient import TestClient


def test_health_endpoints(client: TestClient) -> None:
    """Verifies that the /health endpoints return 200 OK and expected payloads."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

    response = client.get("/health/liveness")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"

    response = client.get("/health/readiness")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_version_endpoint(client: TestClient) -> None:
    """Verifies version check metadata."""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "environment" in data


def test_services_routers_registered(client: TestClient) -> None:
    """Checks that all 7 microservices routers are registered and responsive."""
    services = [
        "governance",
        "identity",
        "ai-platform",
        "media",
        "audit",
        "plugin",
        "decision-intelligence",
    ]

    for service in services:
        response = client.get(
            f"/{service}", headers={"X-User-Role": "System Administrator"}
        )
        assert response.status_code == 200
        assert "service" in response.json()


def test_correlation_headers_propagation(client: TestClient) -> None:
    """Checks that Request and Correlation IDs propagate correctly in responses."""
    # Send request with custom tracking headers
    test_req_id = "test-req-12345"
    test_corr_id = "test-corr-67890"

    response = client.get(
        "/health",
        headers={"X-Request-ID": test_req_id, "X-Correlation-ID": test_corr_id},
    )

    assert response.headers.get("X-Request-ID") == test_req_id
    assert response.headers.get("X-Correlation-ID") == test_corr_id

    # Send request without headers, should generate new ones
    response_gen = client.get("/health")
    assert "X-Request-ID" in response_gen.headers
    assert "X-Correlation-ID" in response_gen.headers
