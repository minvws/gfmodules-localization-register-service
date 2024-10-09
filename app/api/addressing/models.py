from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.data import UraNumber

class Address(BaseModel):
    ura_number: UraNumber
    metadata_endpoint: str


class CommonQueryParams(BaseModel):
    id: UUID | None = Field(None, serialization_alias='_id')
    updated_at: datetime | None = Field(None, serialization_alias='_lastUpdated')


class OrganizationQueryParams(CommonQueryParams):
    active: bool | None = None
    ura_number: str | None = Field(None, serialization_alias="identifier")
    name: str | None = None
    parent_organization_id: UUID | None = Field(None, serialization_alias="partOf")
    type: Literal[
        "prov",
        "dept",
        "team",
        "govt",
        "ins",
        "pay",
        "edu",
        "reli",
        "crs",
        "cg",
        "bus",
        "other",
        None,
    ] = None
    include: Literal["Organization.endpoint", None] = Field(None, serialization_alias='_include')
    rev_include: Literal[
        "Location:organization",
        "OrganizationAffiliation:participating-organization",
        "OrganizationAffiliation:primary-organization",
        None,
    ] = Field(None, serialization_alias='_revInclude')
