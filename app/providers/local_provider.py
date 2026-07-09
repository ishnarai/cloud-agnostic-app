"""
local_provider.py
------------------
Concrete CloudProvider implementation used when running outside any cloud -
e.g. on your own laptop during development, or in a CI test runner.

Why does this exist at all?
Without a "local" provider, developers would be forced to fake being on a
real cloud just to run the app on their laptop. That's exactly the kind of
friction cloud-agnostic design is supposed to eliminate. Treating "local" as
a first-class provider (not a special-cased hack) keeps main.py's logic
completely uniform - it always just asks "give me a provider" and gets one back.
"""

from app.providers.base import CloudProvider


class LocalProvider(CloudProvider):
    def get_provider_name(self) -> str:
        return "Local"

    def get_metadata(self) -> dict:
        return {
            "region": "localhost",
            "service": "Docker / bare metal (development machine)",
        }
