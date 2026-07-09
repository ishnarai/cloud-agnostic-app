"""
test_main.py
------------
Automated tests for the FastAPI app.

Why tests matter specifically for a cloud-agnostic PoC:
The abstraction layer is only trustworthy if we can PROVE every provider
implements the contract correctly. These tests exercise the factory function
directly, which is exactly what would catch a bug like "GcpProvider forgot to
implement get_metadata()" before it ever reached production.

We use FastAPI's TestClient (built on httpx), which lets us call our own
endpoints in-process - no real server or network socket needed. This makes
tests fast and reliable to run in CI (Section 8).
"""

from fastapi.testclient import TestClient

from app.main import app
from app.providers import get_provider
from app.providers.aws_provider import AwsProvider
from app.providers.azure_provider import AzureProvider
from app.providers.gcp_provider import GcpProvider
from app.providers.local_provider import LocalProvider

client = TestClient(app)


def test_health_endpoint_returns_200():
    """The health endpoint must always return HTTP 200 - Kubernetes depends on this."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_endpoint_returns_html():
    """The root endpoint must return HTML, not JSON, per our design decision."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Hello from" in response.text


def test_factory_returns_correct_provider_for_each_known_value():
    """
    This test is the real proof that the abstraction layer works:
    each string input must map to the correct concrete class.
    """
    assert isinstance(get_provider("aws"), AwsProvider)
    assert isinstance(get_provider("azure"), AzureProvider)
    assert isinstance(get_provider("gcp"), GcpProvider)
    assert isinstance(get_provider("local"), LocalProvider)


def test_factory_fails_safe_to_local_for_unknown_value():
    """An unrecognized CLOUD_PROVIDER value must never crash the app."""
    result = get_provider("some-typo-value")
    assert isinstance(result, LocalProvider)


def test_every_provider_implements_the_full_contract():
    """
    Loops through every known provider and confirms each one returns the
    correct TYPES from the interface methods - not just that they don't crash.
    """
    for name in ["aws", "azure", "gcp", "local"]:
        provider = get_provider(name)
        assert isinstance(provider.get_provider_name(), str)
        assert isinstance(provider.get_metadata(), dict)
