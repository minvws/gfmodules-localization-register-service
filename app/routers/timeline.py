import logging
from typing import Any

from fastapi import APIRouter, Depends
from opentelemetry import trace

from pydantic import BaseModel

from app import container
from app.data import DataDomain, Pseudonym
from app.telemetry import get_tracer
from app.timeline.fhir import FHIRException
from app.timeline.timeline_service import TimelineService, TimelineError

logger = logging.getLogger(__name__)
router = APIRouter()


class TimelineRequest(BaseModel):
    """
    Request model for timeline
    """

    pseudonym: str
    data_domain: str


@router.post(
    "/timeline", summary="Search for all timeline events", tags=["timeline_group"]
)
def post_timeline(
    req: TimelineRequest,
    timeline_service: TimelineService = Depends(container.get_timeline_service),
) -> Any:
    span = trace.get_current_span()
    span.update_name(
        f"POST /timeline pseudonym={req.pseudonym} data_domain={req.data_domain}"
    )

    try:
        pseudonym = Pseudonym(req.pseudonym)
    except ValueError:
        raise FHIRException(
            status_code=400, severity="error", code="invalid", msg="Invalid pseudonym"
        )

    data_domain = DataDomain.from_str(req.data_domain)
    if data_domain is None:
        raise FHIRException(
            status_code=400, severity="error", code="invalid", msg="Invalid data domain"
        )

    try:
        with get_tracer().start_as_current_span("retrieve_timeline") as tl_span:
            timeline = timeline_service.retrieve(pseudonym, data_domain)
            tl_span.add_event("timeline_retrieved")
    except TimelineError as e:
        raise FHIRException(
            status_code=400, severity="error", code="invalid", msg=e.message
        )
    ret_value = timeline.dict()
    span.set_attribute("data.number_of_bundles", timeline.total)
    return ret_value
