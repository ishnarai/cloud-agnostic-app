"""
gcp_provider.py
----------------
Concrete CloudProvider implementation for Google Cloud Platform.
"""

import os

from app.providers.base import CloudProvider


class GcpProvider(CloudProvider):
    """
    GCP-specific implementation of the CloudProvider contract.

    PRODUCTION NOTE:
    Real GCP Compute Engine instances expose metadata at
    http://metadata.google.internal/computeMetadata/v1/ (requires a
    "Metadata-Flavor: Google" header). Simulated here for the same reasons
    as the other cloud providers.
    """

    def get_provider_name(self) -> str:
        return "Google Cloud"

    def get_metadata(self) -> dict:
        return {
            "region": os.getenv("GCP_REGION", "asia-south1 (simulated)"),
            "service": "GKE (Google Kubernetes Engine)",
        }
