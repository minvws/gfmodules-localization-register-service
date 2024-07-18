
from pydantic import BaseModel

from app.data import UraNumber


class Address(BaseModel):
    ura_number: UraNumber
    metadata_endpoint: str