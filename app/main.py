"""
main.py
-------
The FastAPI application entrypoint.

Design principle: this file should stay "thin". It wires together routes and
delegates real logic elsewhere (config.py for settings, providers/ for cloud
abstraction). A main.py that's thousands of lines long is a sign the app's
responsibilities weren't separated properly.
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.config import settings
from app.providers import get_provider

# Build the correct provider object ONCE, when the app starts up, using the
# CLOUD_PROVIDER value read in config.py. This single line is where the
# abstraction layer connects to the rest of the app - everything below this
# line refers only to `provider`, never to raw strings or cloud-specific code.
provider = get_provider(settings.CLOUD_PROVIDER)

# Create the FastAPI application instance.
# `title` and `description` show up automatically in the interactive docs at /docs -
# this is one of the "free" benefits of FastAPI mentioned earlier.
app = FastAPI(
    title="Cloud-Agnostic PoC",
    description="A FastAPI app demonstrating cloud-agnostic deployment across AWS, Azure, and GCP.",
    version="1.0.0",
)


@app.get("/", response_class=HTMLResponse)
def read_root() -> str:
    """
    Human-facing route.

    Returns a simple HTML page (not JSON) so that opening this URL in a browser
    gives a readable, demo-friendly result instead of raw text.

    We now use the `provider` object (built once at module load time using
    the factory function) instead of a raw string. Notice this function has
    NO idea whether `provider` is AwsProvider, AzureProvider, GcpProvider, or
    LocalProvider - it only calls the two methods every provider guarantees:
    get_provider_name()  and get_metadata(). This is abstraction in action.
    """
    metadata = provider.get_metadata()

    html_content = f"""
    <html>
        <head>
            <title>{settings.APP_NAME}</title>
        </head>
        <body style="font-family: sans-serif; text-align: center; margin-top: 15%;">
            <h1>Hello from {settings.APP_NAME}</h1>
            <p>Running on cloud provider: <strong>{provider.get_provider_name()}</strong></p>
            <p>Region: {metadata.get("region")}</p>
            <p>Orchestration service: {metadata.get("service")}</p>
        </body>
    </html>
    """
    return html_content


@app.get("/health")
def health_check() -> dict:
    """
    Machine-facing route.

    Kubernetes (and most orchestration platforms) periodically calls a
    "health check" endpoint to decide if a running container is healthy.
    It expects a fast, predictable response - JSON with a simple status field
    is the standard convention, not an HTML page meant for humans.

    We will wire this exact endpoint into k8s/deployment.yaml in Section 6
    as a "liveness probe" and "readiness probe".
    """
    return {
        "status": "ok",
        "cloud_provider": provider.get_provider_name(),
        "metadata": provider.get_metadata(),
    }
