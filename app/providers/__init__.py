"""
providers/__init__.py
----------------------
This file does two things:
1. Marks the `providers` directory as a Python package (required for imports
   like `from app.providers import get_provider` to work).
2. Hosts the factory function `get_provider()`, which is the ONE place in the
   entire codebase that contains "if provider == aws / elif azure / elif gcp"
   branching logic.

Why centralize the branching here instead of in main.py?
This is the core discipline of the whole abstraction layer. If this branching
logic were duplicated in main.py, in a background job, and in a CLI tool later,
adding a fourth cloud provider would require finding and updating every one of
those places. By centralizing it here, adding a new cloud is a two-step change:
  1. Create app/providers/new_provider.py implementing CloudProvider.
  2. Add ONE line to the factory function below.
Nothing else in the codebase needs to change.
"""

from app.providers.base import CloudProvider
from app.providers.aws_provider import AwsProvider
from app.providers.azure_provider import AzureProvider
from app.providers.gcp_provider import GcpProvider
from app.providers.local_provider import LocalProvider


def get_provider(provider_name: str) -> CloudProvider:
    """
    Factory function: given a string (e.g. "aws"), return the matching
    CloudProvider implementation.

    Using a dictionary lookup instead of a long if/elif chain is a common
    Python idiom - it's more concise and, arguably, easier to scan than
    a stack of elif statements.
    """
    providers = {
        "aws": AwsProvider,
        "azure": AzureProvider,
        "gcp": GcpProvider,
        "local": LocalProvider,
    }

    # .get(...) with a fallback to LocalProvider means an unrecognized or
    # missing value never crashes the app - it fails safe to local behavior,
    # which is the least surprising, least destructive default.
    provider_class = providers.get(provider_name, LocalProvider)

    # Note: providers dict stores the CLASS itself (e.g. AwsProvider), not an
    # instance. We call it here - provider_class() - to actually construct
    # the object we return.
    return provider_class()
