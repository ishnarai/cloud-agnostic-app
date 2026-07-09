"""
config.py
---------
Centralized application configuration.

Why this file exists:
Every value that can change between environments (local machine, AWS, Azure, GCP)
should be read from environment variables, NOT hardcoded. This file is the single
place where we read those variables, so the rest of the app never calls
`os.environ` directly — it just imports `settings` from here.

This matters for cloud-agnosticism specifically: switching the deployment target
should only ever require changing environment variables, never editing source code.
"""

import os


class Settings:
    """
    A simple settings container.

    We use a plain class (not a database, not a config file) because for a PoC,
    the entire configuration surface is small. In a larger production app, you'd
    likely use Pydantic's BaseSettings for automatic validation and type coercion -
    we'll mention that as a natural next step in the README.
    """

    # The name of the app, shown in the HTML response.
    APP_NAME: str = os.getenv("APP_NAME", "Orion")

    # This is the single most important variable in the entire project.
    # It tells the application (and later, the CI/CD pipeline) which cloud
    # is currently the deployment target. Valid values: "aws", "azure", "gcp", "local".
    # Defaulting to "local" means if you forget to set it, the app still runs safely
    # on your laptop instead of crashing or guessing.
    CLOUD_PROVIDER: str = os.getenv("CLOUD_PROVIDER", "local").lower()

    # The port the app listens on inside its container.
    # Reading this from env (rather than hardcoding 8000) allows cloud platforms
    # that dynamically assign ports (some PaaS platforms do) to still work.
    PORT: int = int(os.getenv("PORT", "8000"))


# A single shared instance, imported everywhere else in the app.
# This is the standard "singleton settings object" pattern used across
# FastAPI, Django, and most production Python services.
settings = Settings()
