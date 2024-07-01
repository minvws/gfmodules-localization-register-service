import logging
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

from fhir.resources.bundle import Bundle, BundleEntry
from fhir.resources.fhirtypes import Code, UnsignedInt, Id

from app.api.addressing.api import AddressingApi, AddressingError
from app.api.localisation.api import LocalisationApi, LocalisationError
from app.api.localisation.models import LocalisationEntry
from app.api.metadata.api import MetadataApi
from app.api.pseudonym.api import PseudonymApi, PseudonymError
from app.config import get_config
from app.data import DataDomain, Pseudonym
from app.timeline.fhir import OperationOutcome

logger = logging.getLogger(__name__)


class TimelineError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class TimelineService:
    def __init__(
        self,
        localisation_api: LocalisationApi,
        addressing_api: AddressingApi,
        metadata_api: MetadataApi,
        pseudonym_api: PseudonymApi,
    ) -> None:
        self.localisation_api = localisation_api
        self.addressing_api = addressing_api
        self.metadata_api = metadata_api
        self.pseudonym_api = pseudonym_api

    def retrieve(self, pseudonym: Pseudonym, data_domain: DataDomain) -> Bundle:
        # Exchange pseudonyms for localisation and addressing
        config = get_config()

        logger.info(f"Exchanging pseudonym {pseudonym} for localisation")
        try:
            localisation_pseudonym = self.pseudonym_api.exchange(pseudonym, config.localisation_api.provider_id)
        except PseudonymError as e:
            logger.error(f"Failed to exchange pseudonym: {e}")
            raise TimelineError(f"Failed to exchange pseudonym: {e}")

        # Find providers in localisation service and iterate each one
        logger.info(f"Fetching providers for localisation {localisation_pseudonym} and data domain {data_domain}")
        try:
            providers = self.localisation_api.get_providers(localisation_pseudonym, data_domain)
        except LocalisationError as e:
            logger.error(f"Failed to fetch providers from localisation: {e}")
            providers = []

        searchsets = self.threaded_fetch_providers(providers, pseudonym, data_domain)

        return Bundle(  # type: ignore
            resource_type="Bundle",
            id=Id(uuid.uuid4()),
            type=Code("searchset"),
            total=UnsignedInt(len(searchsets)),
            entry=searchsets        # type: ignore
        )

    def fetch_metadata_from_provider(
            self,
            pseudonym: Pseudonym,
            provider: LocalisationEntry,
            data_domain: DataDomain
    ) -> Bundle | OperationOutcome | None:
        """
        Fetch healthcare metadata from a provider
        """
        try:
            # Fetch address for the given provider
            logger.info(f"Fetching addressing from provider {provider.name}")
            address = self.addressing_api.get_addressing(provider.medmij_id, data_domain)
        except AddressingError as e:
            logger.error(f"Failed to fetch addressing from provider {provider}: {e}")
            raise Exception(f"Failed to fetch addressing from provider {provider}: {e}")

        if address is None:
            logger.warning(f"No addressing found for provider {provider.name}")
            raise Exception(f"No addressing found for provider {provider}")

        # Fetch metadata at the found provider address
        try:
            metadata_pseudonym = self.pseudonym_api.exchange(pseudonym, str(address.provider_id))
            return self.metadata_api.search_metadata(
                metadata_pseudonym,
                metadata_endpoint=address.metadata_endpoint,
                data_domain=data_domain,
                provider_id=str(address.provider_id)
            )
        except Exception as e:
            return OperationOutcome(
                issue=[
                    {  # type: ignore
                        "severity": "error",
                        "code": "exception",
                        "details": [
                            {
                                "text": str(e)
                            },
                            {
                                "text": f"{provider.name} ({provider.medmij_id})"
                            }
                        ]
                    }
                ],
            )

    def threaded_fetch_providers(self, providers: list[LocalisationEntry], pseudonym: Pseudonym, data_domain: DataDomain) -> list[BundleEntry]:
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(self.fetch_metadata_from_provider, pseudonym, provider, data_domain)
                for provider in providers
            ]

            searchsets = []
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if isinstance(result, Bundle):
                        searchsets.append(BundleEntry(resource=result))   # type: ignore
                except Exception as e:
                    logger.error(f"Failed to fetch metadata from provider: {e}")
                    searchsets.append(BundleEntry(resource=OperationOutcome(
                        id=Id(uuid.uuid4()),
                        issue=[
                            {  # type: ignore
                                "severity": "error",
                                "code": "exception",
                                "details": {
                                    "text": str(e)
                                }
                            }
                        ],
                    ).dict()))
            return searchsets