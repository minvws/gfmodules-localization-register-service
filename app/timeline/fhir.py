import hashlib
import logging
import uuid
from datetime import datetime
from typing import List

from fastapi import HTTPException
from fhir.resources.fhirtypes import CodeableConceptType
from pydantic import BaseModel

from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.bundle import BundleEntry
from fhir.resources.R4B.practitioner import Practitioner
from fhir.resources.R4B.organization import Organization
from fhir.resources.R4B.reference import Reference
from fhir.resources.R4B.list import List as FhirList
from fhir.resources.R4B.attachment import Attachment
from fhir.resources.R4B.media import Media

from app.api.metadata.models import MetadataEntry
from app.timeline.models import TimelineEntry

logger = logging.getLogger(__name__)


class OperationOutcomeDetail(BaseModel):
    text: str


class OperationOutcomeIssue(BaseModel):
    severity: str
    code: str
    details: OperationOutcomeDetail


class OperationOutcome(BaseModel):
    resourceType: str = "OperationOutcome"
    issue: list[OperationOutcomeIssue]


class FHIRException(HTTPException):
    def __init__(self, status_code: int, severity: str, code: str, msg: str):
        outcome = OperationOutcome(issue=[
            OperationOutcomeIssue(
                severity=severity,
                code=code,
                details=OperationOutcomeDetail(text=msg)
            )
        ])
        super().__init__(status_code=status_code, detail=outcome.model_dump())


def convert_physician_to_practitioner(physician):
    return Practitioner(id=str(physician.ura), name=[{"text": physician.name}])


def convert_healthcare_provider_to_organization(healthcare_provider):
    return Organization(id=str(healthcare_provider.ura), name=healthcare_provider.name)


def metadata_entry_to_fhir(entry: MetadataEntry) -> Bundle:
    practitioner = convert_physician_to_practitioner(entry.evaluation.physician)
    organization = convert_healthcare_provider_to_organization(entry.healthcare_provider)

    bundle = Bundle(
        id=entry.id,
        type="MetadataEntry",
        entry=[
            BundleEntry(resource=practitioner),
            BundleEntry(resource=organization),
        ]
    )

    for metadata_entry in entry.metadata['images'] or []:
        media = Media(
            id=metadata_entry['id'],
            status="completed",
            type=CodeableConceptType(
                coding=[{
                    "system": "http://loinc.org",
                    "code": "http://loinc.org",
                    "display": "Color photograph of body structure",
                }],
            ),
            subject=Reference(
                reference=f"Patient/123456789",
                type="Patient",
            ),
            height=786,
            width=1024,
            content=Attachment(
                contentType="image/jpeg",
                url=metadata_entry['url'],
                title="Title or filename of the media object",
            ),
            note=[{"text": metadata_entry['description']}],
        )
        bundle.entry.append(BundleEntry(resource=media))

    return bundle


def to_hash(value: bytes) -> str:
    """
    Create a SHA256 hash from the given value
    """
    m = hashlib.sha256()
    m.update(value)
    return m.hexdigest()


def timeline_to_fhir(timeline: List[TimelineEntry]) -> Bundle:
    # The bundle will contain all elements in a flat structure
    bundle = Bundle(
        resourceType="Bundle",
        type="collection",
        entry=[]
    )

    # Timeline list will hold a list of organisations that have contained timeline entries
    timeline_list = FhirList(
        resourceType="List",
        title="Timeline",
        mode="working",
        status="current",
        id=str(uuid.uuid4()),
        entry=[], # type: ignore
        date=datetime.now(),
    )
    bundle.entry.append(BundleEntry(resource=timeline_list))

    # Quickly return when there is no timeline data found
    if timeline is None or len(timeline) == 0:
        timeline_list.emptyReason = "No data available"
        timeline_list.status = "not-found"
        return bundle

    # Iterate all (organization) entries and collect the timeline entries
    timeline_list.status = "current"
    for entry in timeline:

        # Create a hash for the organization id, as our IDs are not compatible with FHIR
        org_hash = to_hash(entry.healthcare_provider_medmij_id.encode())

        # Create an organization and append to the bundle and timeline list
        org = Organization(
            id=org_hash,
            # id=[{"value": f"Organization/{org_hash}"}],
            name=entry.healthcare_provider_name,
            contained=[],
        )
        bundle.entry.append(BundleEntry(resource=org))
        timeline_list.entry.append(Reference(
            reference=f"Organization/{org_hash}",
            type="Organization",
        ))

        if entry.error:
            org.error = True
            org.error_msg = entry.error_msg
            continue

        # Iterate all metadata entries and add them to the bundle and reference them in the organization
        for metadata_entry in entry.items.values() or []:
            metadata_entry = metadata_entry_to_fhir(metadata_entry.entry)

            bundle.entry.append(BundleEntry(resource=metadata_entry))
            org.contained.append(Reference(
                reference=f"MetadataEntry/{metadata_entry.id}",
                type="MetadataEntry",
            ))

    return bundle

