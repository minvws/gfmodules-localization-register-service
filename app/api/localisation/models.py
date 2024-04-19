from pydantic import BaseModel

from app.data import DataDomain


class LocalisationEntry(BaseModel):
    medmij_id: str
    name: str
    data_domain: DataDomain