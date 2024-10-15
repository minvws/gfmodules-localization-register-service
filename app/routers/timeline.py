import logging
from typing import Any

from fastapi import APIRouter, Depends
from opentelemetry import trace

from app import container
from app.data import DataDomain, Pseudonym
from app.telemetry import get_tracer
from app.timeline.fhir import FHIRException
from app.timeline.timeline_service import TimelineService, TimelineError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/fhir/{fhir_type}/_search",
            summary="Search for all timeline events",
            tags=["timeline_group"]
            )
def post_timeline(
    fhir_type: str,
    pseudonym: str,
    timeline_service: TimelineService = Depends(container.get_timeline_service)
) -> Any:
    span = trace.get_current_span()
    span.update_name(f"POST /fhir/{fhir_type}/_search pseudonym={pseudonym}")

    try:
        p = Pseudonym(pseudonym)
    except ValueError:
        raise FHIRException(
            status_code=400, severity="error", code="invalid", msg="Invalid pseudonym"
        )

    data_domain = DataDomain.from_fhir(fhir_type)
    if data_domain is None:
        raise FHIRException(
            status_code=400, severity="error", code="invalid", msg="Invalid data domain"
        )

    try:
        with get_tracer().start_as_current_span("retrieve_timeline") as tl_span:
            timeline = timeline_service.retrieve(p, data_domain)
            tl_span.add_event("timeline_retrieved")
    except TimelineError as e:
        raise FHIRException(
            status_code=400, severity="error", code="invalid", msg=e.message
        )
    ret_value = timeline.dict()
    span.set_attribute("data.number_of_bundles", timeline.total)
    return ret_value
