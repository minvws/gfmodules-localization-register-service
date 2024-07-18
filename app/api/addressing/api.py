import logging

import requests
from requests import HTTPError

from app.api.addressing.models import Address
from app.data import DataDomain, UraNumber

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

    def get_addressing(self, ura_number: UraNumber, data_domain: DataDomain) -> Address | None:
        try:
            logger.info(f"Fetching addressing for ura number {str(ura_number)} / {str(data_domain)}")

            req = requests.post(
                f"{self.endpoint}/metadata_endpoint",
                json={
                    "ura_number": str(ura_number),
                    "data_domain": str(data_domain),
                },
                timeout=self.timeout,
                cert=(self.mtls_cert, self.mtls_key),
                verify=self.mtls_ca
            )
        except (Exception, HTTPError) as e:
            raise AddressingError(f"Failed to fetch addressing: http error: {e}")

        if req.status_code == 404:
            return None

        if req.status_code == 422:
            raise AddressingError(f"Invalid request: {req.text}")

        if req.status_code != 200:
            raise AddressingError(f"Failed to fetch addressing: http status code: {req.status_code}")

        data = req.json()
        return Address(
            ura_number=ura_number,
            metadata_endpoint=data['endpoint'],
        )
