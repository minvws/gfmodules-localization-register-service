import logging
from typing import List

from app.api.addressing.api import AddressingApi, AddressingError
from app.api.localisation.api import LocalisationApi, LocalisationError
from app.api.localisation.models import LocalisationEntry
from app.api.metadata.api import MetadataApi
from app.api.metadata.models import Metadata
from app.api.pseudonym.api import PseudonymApi, PseudonymError
from app.config import get_config
from app.data import DataDomain, Pseudonym
from app.timeline.models import TimelineEntry

logger = logging.getLogger(__name__)


class TimelineError(Exception):
    pass


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

    def retrieve(self, pseudonym: Pseudonym, data_domain: DataDomain) -> List[TimelineEntry]:
        timeline = []

        # Exchange pseudonyms for localisation and addressing
        config = get_config()

        logger.info(f"Exchanging pseudonym {pseudonym} for localisation and addressing")
        try:
            localisation_pseudonym = self.pseudonym_api.exchange(pseudonym, config.localisation_api.provider_id)
            addressing_pseudonym = self.pseudonym_api.exchange(pseudonym, config.addressing_api.provider_id)
        except PseudonymError as e:
            logger.error(f"Failed to exchange pseudonyms: {e}")
            raise TimelineError(f"Failed to exchange pseudonyms: {e}")

        # Find providers in localisation service and iterate each one
        logger.info(f"Fetching providers for localisation {localisation_pseudonym} and data domain {data_domain}")
        try:
            providers = self.localisation_api.get_providers(localisation_pseudonym, data_domain)
        except LocalisationError as e:
            logger.error(f"Failed to fetch providers from localisation: {e}")
            providers = []

        for provider in providers:
            # @TODO: make this async and collect at the end
            logger.info(f"Fetching metadata from provider {provider.name}")
            entry = self.fetch_metadata_from_provider(addressing_pseudonym, provider, data_domain)
            if entry is None:
                logger.warning(f"Failed to fetch metadata from provider {provider.name}")

            timeline.append(TimelineEntry(
                healthcare_provider_name=provider.name,
                healthcare_provider_medmij_id=provider.medmij_id,
                error=True if entry is None else False,
                error_msg="Failed to fetch metadata" if entry is None else None,
                entry=entry
            ))

        return timeline

    def fetch_metadata_from_provider(self, addressing_pseudonym: Pseudonym, provider: LocalisationEntry, data_domain: DataDomain) -> dict[str,Metadata]|None:
        """
        Fetch healthcare metadata from a provider
        """
        try:
            # Fetch address for the given provider
            logger.info(f"Fetching addressing from provider {provider.name}")
            address = self.addressing_api.get_addressing(provider.medmij_id, data_domain)
        except AddressingError as e:
            logger.error(f"Failed to fetch addressing from provider {provider}: {e}")
            return None

        # Fetch metadata at the found provider address
        metadata_pseudonym = self.pseudonym_api.exchange(addressing_pseudonym, str(address.provider_id))
        metadata = self.metadata_api.get_metadata(
            metadata_pseudonym,
            metadata_endpoint=address.metadata_endpoint,
        )

        return metadata
