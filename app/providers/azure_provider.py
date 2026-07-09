"""
azure_provider.py
------------------
Concrete CloudProvider implementation for Microsoft Azure.
"""

import os

from app.providers.base import CloudProvider


class AzureProvider(CloudProvider):
    """
    Azure-specific implementation of the CloudProvider contract.

    PRODUCTION NOTE:
    Real Azure VMs expose an Instance Metadata Service (IMDS) at
    http://169.254.169.254/metadata/instance?api-version=2021-02-01
    (requires a "Metadata: true" header). This class simulates that response
    using environment variables for the same reasons described in aws_provider.py.
    """

    def get_provider_name(self) -> str:
        return "Azure"

    def get_metadata(self) -> dict:
        return {
            "region": os.getenv("AZURE_REGION", "centralindia (simulated)"),
            "service": "AKS (Azure Kubernetes Service)",
        }
