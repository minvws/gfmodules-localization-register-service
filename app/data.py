import uuid
from enum import Enum
from typing import Optional


# DataDomain definitions
class DataDomain(Enum):
    Unknown = 'unknown'
    BeeldBank = 'beeldbank'
    Medicatie = 'medicatie'

    @classmethod
    def from_str(cls, label: str) -> Optional['DataDomain']:
        try:
            return cls(label.lower())
        except ValueError:
            return None

    def to_fhir(self) -> str:
        if self == DataDomain.BeeldBank:
            return 'ImagingStudy'
        if self == DataDomain.Medicatie:
            return 'MedicationRequest'
        return ""

# Pseudonym for a hashed BSN
Pseudonym = uuid.UUID


def str_to_pseudonym(pseudonym: str) -> Pseudonym|None:
    """
    Convert a string to a UUID pseudonym
    """
    try:
        return uuid.UUID(pseudonym)
    except ValueError:
        return None


# Healthcare ID
HealthcareID = str
