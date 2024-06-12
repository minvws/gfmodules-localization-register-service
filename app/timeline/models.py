from typing import Optional

from pydantic import BaseModel

from app.api.metadata.models import Metadata


class TimelineEntry(BaseModel):
    healthcare_provider_name: str
    healthcare_provider_medmij_id: str
    error: bool = False
    error_msg: Optional[str] = None
    items: Optional[dict[str, Metadata]] = None

