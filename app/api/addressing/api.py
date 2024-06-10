import logging
import uuid

import requests
from requests import HTTPError

from app.api.addressing.models import Address
from app.api.localisation.api import LocalisationError
from app.data import DataDomain

logger = logging.getLogger(__name__)


class AddressingError(Exception):
    pass


class AddressingApi:
    def __init__(self, endpoint: str, timeout: int, mtls_cert: str, mtls_key: str, mtls_ca: str, metadata_endpoint: str):
        self.endpoint = endpoint
        self.timeout = timeout
        self.mtls_cert = mtls_cert
        self.mtls_key = mtls_key
        self.mtls_ca = mtls_ca
        self.metadata_endpoint = metadata_endpoint

    def get_addressing(self, provider_medmij_id: str, data_domain: DataDomain) -> Address | None:
        try:
            logger.info(f"Fetching addressing for provider {provider_medmij_id} / {data_domain}")

            req = requests.post(
                f"{self.endpoint}/metadata_endpoint",
                json={
                    "provider_id": provider_medmij_id,
                    "data_domain": str(data_domain.value),
                },
                timeout=self.timeout,
                cert=(self.mtls_cert, self.mtls_key),
                verify=self.mtls_ca
            )
        except (Exception, HTTPError) as e:
            raise LocalisationError(f"Failed to fetch addressing: http error: {e}")

        if req.status_code == 404:
            return None

        if req.status_code != 200:
            raise LocalisationError(f"Failed to fetch addressing: http status code: {req.status_code}")

        data = req.json()
        return Address(
            # Need UUID5 in order to convert the pseudonym to a deterministic UUID
            provider_id=uuid.uuid5(uuid.NAMESPACE_DNS, provider_medmij_id),
            metadata_endpoint=data['endpoint'],
        )