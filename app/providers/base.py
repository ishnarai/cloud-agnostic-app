"""
base.py
-------
Defines the CloudProvider interface (contract).

Why an interface at all?
Without this, nothing forces the AWS, Azure, and GCP provider classes to expose
the same methods. If AwsProvider had `.name()` but AzureProvider had `.get_name()`,
main.py could not treat them interchangeably - it would need to know which
concrete class it received, which defeats the entire purpose of abstraction.

We use Python's `abc` (Abstract Base Class) module to make this enforceable:
if a subclass forgets to implement a required method, Python raises an error
the moment you try to create that subclass - not silently at some later,
harder-to-debug point.
"""

from abc import ABC, abstractmethod


class CloudProvider(ABC):
    """
    Abstract base class that every cloud provider implementation must extend.

    Any class inheriting from CloudProvider MUST implement every method marked
    with @abstractmethod below, or Python will raise:
        TypeError: Can't instantiate abstract class X with abstract methods ...
    """

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Return a short, human-readable name for this provider.
        Example: "AWS", "Azure", "Google Cloud", "Local".
        """
        raise NotImplementedError

    @abstractmethod
    def get_metadata(self) -> dict:
        """
        Return a dictionary of provider-specific metadata.

        This is intentionally a generic dict rather than a rigid schema, because
        each cloud exposes different useful metadata (AWS: instance ID and
        availability zone; Azure: resource group and VM size; GCP: project ID
        and zone). The CALLER (main.py) doesn't need to know or care about the
        exact keys - it just displays whatever is returned.

        In a real production, non-PoC system, you might tighten this into a
        typed Pydantic model instead of a loose dict, once the shape stabilizes.
        """
        raise NotImplementedError
