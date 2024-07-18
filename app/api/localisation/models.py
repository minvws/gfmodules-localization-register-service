from pydantic import BaseModel

from app.data import DataDomain, UraNumber


class LocalisationEntry(BaseModel):
    ura_number: UraNumber
    name: str
    data_domain: DataDomain