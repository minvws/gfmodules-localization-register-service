import uuid
from typing import Type, Any

import requests
from fhir.resources.bundle import Bundle, BundleEntry
from fhir.resources.fhirtypes import Code, UnsignedInt, Id
from fhir.resources.imagingstudy import ImagingStudy, ImagingStudySeries, ImagingStudySeriesPerformer
from fhir.resources.organization import Organization
from fhir.resources.patient import Patient
from fhir.resources.practitioner import Practitioner
from fhir.resources.reference import Reference
from fhir.resources.resource import Resource
from requests import HTTPError

from app.data import Pseudonym, DataDomain


class MetadataApiException(Exception):
    pass


class MetadataApi:
    def __init__(self, timeout: int, mtls_cert: str, mtls_key: str, mtls_ca: str):
        self.timeout = timeout
        self.mtls_cert = mtls_cert
        self.mtls_key = mtls_key
        self.mtls_ca = mtls_ca

    def search_metadata(self, pseudonym: Pseudonym, metadata_endpoint: str, data_domain: DataDomain) -> Bundle:
        """
        Retrieves metadata for a given pseudonym from the metadata service
        """
        try:
            # Fhir API: resource found in endpoint/{fhir-resource}/_search
            req = requests.get(
                f"{metadata_endpoint}/{data_domain.to_fhir()}/_search",
                params={"pseudonym": str(pseudonym)},
                timeout=self.timeout,
            )
        except HTTPError as e:
            raise MetadataApiException(f"Metadata register returned unexpected HTTP error: {e}")
        except Exception as e:
            raise MetadataApiException(f"Metadata register returned unexpected error: {e}")

        if req.status_code != 200:
            raise MetadataApiException(f"Metadata register returned unexpected status code: {req.status_code}")

        metadata = req.json()

        # Resources are the main resources that are returned
        resources = {}
        # Linked resources are resources that are linked to the main resources
        linked_resources = dict[str, Any]()
        if "entry" in metadata:
            for entry in metadata["entry"]:
                if entry["resource"]["resourceType"] == "ImagingStudy":
                    obj = ImagingStudy.parse_obj(entry["resource"])

                    # Add imagingstudy as resource
                    key = "ImagingStudy/" + obj.id
                    resources[key] = obj

                    if isinstance(obj.subject, Reference):
                        # Add patient
                        ref_id = obj.subject.reference
                        if ref_id.startswith("urn:uuid:"):
                            ref_id = "Patient/" + ref_id[9:]
                        if obj.subject.display is None:
                            # when the display is set, there is no need to fetch the resource itself for the timeline.
                            patient = self.get_metadata_resource(metadata_endpoint, Patient, ref_id)
                            linked_resources[ref_id] = patient

                    for series_entry in obj.series:
                        if not isinstance(series_entry, ImagingStudySeries):
                            continue
                        if series_entry.performer is None:
                            continue
                        for ref in series_entry.performer:
                            if not isinstance(ref, ImagingStudySeriesPerformer):
                                continue
                            if ref.actor is None:
                                continue
                            if not isinstance(ref.actor, Reference):
                                continue
                            if ref.actor.reference is None:
                                continue
                            if ref.actor.type is None:
                                continue
                            if ref.actor.display is not None:
                                # when the display is set, there is no need to fetch the resource itself for the timeline.
                                continue

                            # Add practitioner
                            if ref.actor.type == "Practitioner":
                                ref_id = ref.actor.reference
                                if ref.actor.reference.startswith("urn:uuid:"):
                                    ref_id = "Practitioner/" + ref.actor.reference[9:]
                                if ref_id not in resources:
                                    practitioner = self.get_metadata_resource(metadata_endpoint, Practitioner, ref_id)
                                    linked_resources[ref_id] = practitioner

                            # Add organization
                            if ref.actor.type == "Organization":
                                ref_id = ref.actor.reference
                                if ref.actor.reference.startswith("urn:uuid:"):
                                    ref_id = "Organization/" + ref.actor.reference[9:]
                                if ref_id not in resources:
                                    organization = self.get_metadata_resource(metadata_endpoint, Organization, ref_id)
                                    linked_resources[ref_id] = organization

        entries = []
        for res in resources.values():
            entries.append(BundleEntry(resource=res.dict(), search=dict(mode="match")))  # type: ignore
        for res in linked_resources.values():
            entries.append(BundleEntry(resource=res.dict(), search=dict(mode="include")))  # type: ignore

        # Somehow it would be nice if we actually can add the provider id in the searchset as well, as this can provide
        # additional information to the caller
        return Bundle(
            resource_type="Bundle",
            id=Id(uuid.uuid4()),
            type=Code("searchset"),
            total=UnsignedInt(len(resources)),
            entry=entries       # type: ignore
        )

    def get_metadata_resource(self,
                              metadata_endpoint: str,
                              resource_cls: Type[Resource],
                              resource_id: str) -> Resource:
        try:
            req = requests.get(
                f"{metadata_endpoint}/{resource_id}",
                timeout=self.timeout,
            )
        except (Exception, HTTPError) as e:
            raise MetadataApiException(f"Failed to fetch metadata resource: {e}")

        if req.status_code != 200:
            raise MetadataApiException(f"Failed to fetch metadata resource: {req.status_code}")

        resource = req.json()
        return resource_cls.parse_obj(resource)
