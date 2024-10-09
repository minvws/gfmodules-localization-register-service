import json
import unittest

import pytest
from fhir.resources.R4B.endpoint import Endpoint
from fhir.resources.R4B.organization import Organization
from mypy.test.helpers import assert_equal

from app.api.addressing.api import AddressingApi


class TestAddressingApi(unittest.TestCase):
    addressing_api = AddressingApi(
        endpoint='random_url',
        timeout=0,
        mtls_cert='',
        mtls_key='',
        mtls_ca='',
    )

    def test_parse_response(self) -> None:
        sample_organization = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Organization",
                        "id": "f001",
                        "active": True,
                        "name": "Some Test Corporation",
                        "address": [
                            {
                                "country": "Test"
                            }
                        ]
                    }
                }
            ]
        }

        sample_endpoint = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Endpoint",
                        "id": "62428",
                        "identifier": [
                            {
                                "system": "http://example.org/enpoint-identifier",
                                "value": "epcp12"
                            }
                        ],
                        "status": "active",
                        "connectionType": {
                            "system": "http://terminology.hl7.org/CodeSystem/endpoint-connection-type",
                            "code": "hl7-fhir-rest"
                        },
                        "name": "Health Intersections CarePlan Hub",
                        "managingOrganization": {
                            "reference": "Organization/62427"
                        },
                        "payloadType": [
                            {
                                "coding": [
                                    {
                                        "system": "http://hl7.org/fhir/resource-types",
                                        "code": "CarePlan"
                                    }
                                ]
                            }
                        ],
                        "payloadMimeType": ["application/fhir+xml"],
                        "address": "http://fhir3.healthintersections.com.au/open/CarePlan"
                    }
                }
            ]
        }

        assert isinstance(self.addressing_api._parse_response(sample_organization), Organization)
        assert_equal(sample_organization.get('entry')[0].get('resource'),  # type: ignore
                     self.addressing_api._parse_response(sample_organization))
        assert isinstance(self.addressing_api._parse_response(sample_endpoint), Endpoint)
        assert (json.dumps(sample_endpoint.get('entry')[0].get('resource'))  # type: ignore
                == self.addressing_api._parse_response(
                    sample_endpoint).json())
        with pytest.raises(Exception):
            self.addressing_api._parse_response({"resourceType": "RANDOM"})
