import logging
import uuid

from app.api.addressing.models import Address
from app.data import DataDomain

logger = logging.getLogger(__name__)


class AddressingError(Exception):
    pass


class AddressingApi:
    def __init__(self, endpoint: str, timeout: int, mtls_cert: str, mtls_key: str, mtls_ca: str):
        self.endpoint = endpoint
        self.timeout = timeout
        self.mtls_cert = mtls_cert
        self.mtls_key = mtls_key
        self.mtls_ca = mtls_ca

    def get_addressing(self, provider_medmij_id: str, data_domain: DataDomain) -> Address:
        logger.info(f"Fetching addressing for provider {provider_medmij_id}")

        # We use a fixed provider to simulate that addressing cannot be found
        if provider_medmij_id == "fysio.amsterdam@medmij":
            raise AddressingError("Addressing not available for provider")

        return Address(
            # Needed in order to convert the pseudonym
            provider_id=uuid.uuid4(),
            metadata_endpoint=f"{self.endpoint}/drs/{provider_medmij_id}/{data_domain.value}",
        )