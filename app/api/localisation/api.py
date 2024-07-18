import logging
from typing import List

import requests
from requests import HTTPError

from app.api.localisation.models import LocalisationEntry
from app.data import Pseudonym, DataDomain, UraNumber

logger = logging.getLogger(__name__)


class LocalisationError(Exception):
    pass


class LocalisationApi:
    def __init__(self, endpoint: str, timeout: int, mtls_cert: str, mtls_key: str, mtls_ca: str):
        self.endpoint = endpoint
        self.timeout = timeout
        self.mtls_cert = mtls_cert
        self.mtls_key = mtls_key
        self.mtls_ca = mtls_ca

    def get_providers(self, pseudonym: Pseudonym, data_domain: DataDomain) -> List[LocalisationEntry]:
        try:
            logger.info(f"Fetching localisation for pseudonym {str(pseudonym)} and data domain {str(data_domain)}")

            req = requests.post(
                f"{self.endpoint}/info",
                json={
                    "pseudonym": str(pseudonym),
                    "data_domain": str(data_domain),
                },
                timeout=self.timeout,
                cert=(self.mtls_cert, self.mtls_key),
                verify=self.mtls_ca,
            )
        except (Exception, HTTPError) as e:
            raise LocalisationError(f"Failed to fetch localisation: http error: {e}")

        if req.status_code == 404:
            return []

        if req.status_code == 422:
            raise LocalisationError(f"Failed to fetch localisation: http status code: {req.status_code} {req.text}")

        if req.status_code != 200:
            raise LocalisationError(f"Failed to fetch localisation: http status code: {req.status_code}")

        ret = []
        data = req.json()
        for entry in data:
            localisation_entry = self.hydrate_to_localisation(entry)
            if localisation_entry is not None:
                ret.append(localisation_entry)
        return ret

    @staticmethod
    def hydrate_to_localisation(data: dict[str, str]) -> LocalisationEntry | None:
        try:
            return LocalisationEntry(
                ura_number=UraNumber(data['ura_number']),
                name=data['name'] if 'name' in data else data['ura_number'],
                data_domain=DataDomain(data['data_domain']),
            )
        except KeyError:
            return None
