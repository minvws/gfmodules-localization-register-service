from typing import Any

import requests
from requests import HTTPError

from app.api.metadata.models import Metadata, MetadataEntry
from app.data import Pseudonym


class MetadataApi:
    def __init__(self, endpoint: str, timeout: int, mtls_cert: str, mtls_key: str, mtls_ca: str):
        self.endpoint = endpoint
        self.timeout = timeout
        self.mtls_cert = mtls_cert
        self.mtls_key = mtls_key
        self.mtls_ca = mtls_ca

    def get_metadata(self, pseudonym: Pseudonym, metadata_endpoint: str) -> dict[str, Metadata]:
        """
        Retrieves metadata for a given pseudonym from the metadata service
        """
        try:
            req = requests.get(
                f"{metadata_endpoint}",
                params={"pseudonym": str(pseudonym)},
                timeout=self.timeout,
            )
        except (Exception, HTTPError) as e:
            raise ValueError(f"Failed to fetch metadata: {e}")

        if req.status_code != 200:
            raise ValueError(f"Failed to fetch metadata: {req.status_code}")

        data = req.json()
        return self.hydrate_to_metadata(data)

    @staticmethod
    def hydrate_to_metadata(data: Any) -> dict[str, Metadata]:
        """
        Converts the raw data from the metadata service to a dictionary of Metadata objects
        """
        ret = {}
        entry = MetadataEntry(**data)
        ret[data['id']] = Metadata(id=data['id'], error=False, error_msg="", entry=entry)

        return ret

