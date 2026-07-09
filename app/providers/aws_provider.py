"""
aws_provider.py
----------------
Concrete CloudProvider implementation for Amazon Web Services.
"""

import os

from app.providers.base import CloudProvider


class AwsProvider(CloudProvider):
    """
    AWS-specific implementation of the CloudProvider contract.

    PRODUCTION NOTE:
    Real AWS EC2 instances expose an "Instance Metadata Service" (IMDS) at the
    special link-local address http://169.254.169.254/latest/meta-data/. In a
    real deployment, this class would make an HTTP GET request to that address
    to fetch the real instance ID, availability zone, etc.

    Since this PoC won't always be running on an actual EC2 instance while you
    develop/test it, we simulate that data here using environment variables,
    with clearly-labeled placeholder defaults. This keeps the CODE PATH
    realistic (this is exactly where the real HTTP call would go) without
    requiring you to have a live AWS account just to run the app locally.
    """

    def get_provider_name(self) -> str:
        return "AWS"

    def get_metadata(self) -> dict:
        # In production, replace the os.getenv(...) calls below with real
        # calls to the AWS IMDS endpoint, e.g.:
        #
        #   import requests
        #   region = requests.get(
        #       "http://169.254.169.254/latest/meta-data/placement/region"
        #   ).text
        #
        return {
            "region": os.getenv("AWS_REGION", "ap-south-1 (simulated)"),
            "service": "EKS (Elastic Kubernetes Service)",
        }
