import uuid

from pydantic import BaseModel


class Address(BaseModel):
    provider_id: uuid.UUID
    metadata_endpoint: str