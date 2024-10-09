import logging
from typing import Any, Union
from urllib.parse import urlencode

import requests
from fhir.resources.R4B.bundle import Bundle, BundleEntry
from fhir.resources.R4B.endpoint import Endpoint
from fhir.resources.R4B.organization import Organization
from fhir.resources.R4B.reference import Reference
from pydantic.v1 import ValidationError
from requests import HTTPError, Response

from app.api.addressing.models import Address, OrganizationQueryParams
from app.data import DataDomain, UraNumber

logger = logging.getLogger(__name__)


class AddressingError(Exception):
    pass


class RequestError(AddressingError):
    def __init__(self, req: Response):
        super().__init__(f"Failed to retrieve addressing resource: {req.status_code}, details: {req.text}")


class AddressingApi:
    def __init__(self, endpoint: str, timeout: int, mtls_cert: str, mtls_key: str, mtls_ca: str):
        self.endpoint = endpoint
        self.timeout = timeout
        self.mtls_cert = mtls_cert
        self.mtls_key = mtls_key
        self.mtls_ca = mtls_ca

    def get_addressing(self, ura_number: UraNumber, _data_domain: DataDomain) -> Address:
        org_params = OrganizationQueryParams(
            id=None,
            updated_at=None,
            parent_organization_id=None,
            rev_include=None,
            ura_number=str(ura_number),
            include="Organization.endpoint",
        )

        organization = self._find_matching_care_services(org_params)

        org_endpoint = None

        if isinstance(organization, Organization):
            if organization.endpoint is None or len(organization.endpoint) == 0:
                raise AddressingError("Organization Endpoint not found")
            org_endpoint = organization.endpoint[0]  # Timeline service for now only works with one endpoint
            if isinstance(org_endpoint, Reference):
                org_endpoint = org_endpoint.reference

        if org_endpoint is None:
            raise AddressingError("Did not get Endpoint back")

        endpoint = self._retrieve_care_service_resource(str(org_endpoint))

        if isinstance(endpoint, Endpoint):
            if endpoint.address is None:
                raise AddressingError("Found Endpoint has no address")

            return Address(  # Create timeline address for now
                ura_number=ura_number,
                metadata_endpoint=endpoint.address,
            )
        raise AddressingError("Getting addressing failed")

    # https://profiles.ihe.net/ITI/mCSD/ITI-90.html#239041-find-matching-care-services-request-message
    def _find_matching_care_services(self, params: OrganizationQueryParams) -> Organization:
        query_params = urlencode(params.model_dump(by_alias=True, exclude_none=True))
        url = self.endpoint + "/Organization"
        try:
            logger.info("Finding matching care services")
            req = requests.get(url=url, params=query_params, timeout=self.timeout,
                               cert=(self.mtls_cert, self.mtls_key),
                               verify=self.mtls_ca)
        except (Exception, HTTPError) as e:
            raise AddressingError(f"Failed to fetch matching care services: {e}")
        if req.status_code != 200 or req.json() is None:
            raise RequestError(req)
        resource = self._parse_response(req.json())
        if isinstance(resource, Organization):
            return resource
        raise RequestError(req)

    # https://profiles.ihe.net/ITI/mCSD/ITI-90.html#239043-retrieve-care-services-resource-message
    def _retrieve_care_service_resource(self, query: str) -> Endpoint:
        url = self.endpoint + "/" + query
        try:
            logger.info("Retrieving care services resource")
            req = requests.get(url=url, timeout=self.timeout,
                               cert=(self.mtls_cert, self.mtls_key),
                               verify=self.mtls_ca)
        except (Exception, HTTPError) as e:
            raise AddressingError(f"Failed to retrieve care services resource: http error: {e}")
        if req.status_code != 200 or req.json() is None:
            raise RequestError(req)
        resource = self._parse_response(req.json())
        if isinstance(resource, Endpoint):
            return resource
        raise RequestError(req)

    @staticmethod
    def _parse_response(response: dict[str, Any]) -> Union[Endpoint | Organization]:
        try:
            bundle = Bundle.parse_obj(response)
            for entry in bundle.entry:
                if isinstance(entry, BundleEntry):
                    resource = entry.resource
                    if isinstance(resource, Union[Endpoint | Organization]):
                        return resource  # Timeline service for now only works with one endpoint
            raise AddressingError("Bundle has incorrect entries")
        except ValidationError as e:
            raise AddressingError(f"Nothing could be parsed from the addressing service {e}")
