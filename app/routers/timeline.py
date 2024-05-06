import logging
import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from opentelemetry import trace

from pydantic import BaseModel

from app import container
from app.data import str_to_pseudonym, DataDomain
from app.telemetry import get_tracer
from app.timeline.models import TimelineEntry
from app.timeline.timeline_service import TimelineService, TimelineError

logger = logging.getLogger(__name__)
router = APIRouter()


class TimelineRequest(BaseModel):
    """
    Request model for timeline
    """
    pseudonym: str
    data_domain: str


class TimelineResponse(BaseModel):
    """
    Response model for timeline
    """
    id: uuid.UUID
    creation_date: datetime
    pseudonym: str
    timeline: List[TimelineEntry]


@router.post("/timeline",
            summary="Search for all timeline events",
            tags=["timeline_group"]
            )
def post_timeline(
    req: TimelineRequest,
    timeline_service: TimelineService = Depends(container.get_timeline_service)
) -> TimelineResponse:

    span = trace.get_current_span()
    span.set_attribute("data.pseudonym", req.pseudonym)
    span.set_attribute("data.data_domain", req.data_domain)

    pseudonym = str_to_pseudonym(req.pseudonym)
    if pseudonym is None:
        raise HTTPException(status_code=400, detail="Invalid pseudonym")

    data_domain = DataDomain.from_str(req.data_domain)
    if data_domain is None:
        raise HTTPException(status_code=400, detail="Invalid data domain")

    try:
        with get_tracer().start_as_current_span("retrieve_timeline") as tl_span:
            timeline = timeline_service.retrieve(pseudonym, data_domain)
            tl_span.add_event("timeline_retrieved")
    except TimelineError as e:
        raise HTTPException(status_code=400, detail=e)

    return TimelineResponse(
        id=uuid.uuid4(),
        creation_date=datetime.now(),
        pseudonym=req.pseudonym,
        timeline=timeline
    )
