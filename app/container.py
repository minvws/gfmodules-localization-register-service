
import inject

from app.api.addressing.api import AddressingApi
from app.api.localisation.api import LocalisationApi
from app.api.metadata.api import MetadataApi
from app.api.pseudonym.api import PseudonymApi
from app.timeline.timeline_service import TimelineService
from db.db import Database
from config import get_config


def container_config(binder: inject.Binder) -> None:
    config = get_config()

    db = Database(dsn=config.database.dsn)
    binder.bind(Database, db)

    cfg = config.pseudonym_api
    pseudonym_api = PseudonymApi(
        endpoint=cfg.endpoint,
        timeout=cfg.timeout,
        mtls_cert=cfg.mtls_cert,
        mtls_key=cfg.mtls_key,
        mtls_ca=cfg.mtls_ca
    )
    # binder.bind(PseudonymApi, pseudonym_api)

    cfg = config.localisation_api
    localisation_api = LocalisationApi(
        endpoint=cfg.endpoint,
        timeout=cfg.timeout,
        mtls_cert=cfg.mtls_cert,
        mtls_key=cfg.mtls_key,
        mtls_ca=cfg.mtls_ca
    )

    cfg = config.addressing_api
    addressing_api = AddressingApi(
        endpoint=cfg.endpoint,
        timeout=cfg.timeout,
        mtls_cert=cfg.mtls_cert,
        mtls_key=cfg.mtls_key,
        mtls_ca=cfg.mtls_ca
    )

    cfg = config.metadata_api
    metadata_api = MetadataApi(
        endpoint=cfg.endpoint,
        timeout=cfg.timeout,
        mtls_cert=cfg.mtls_cert,
        mtls_key=cfg.mtls_key,
        mtls_ca=cfg.mtls_ca
    )

    timeline_service = TimelineService(
        pseudonym_api=pseudonym_api,
        localisation_api=localisation_api,
        addressing_api=addressing_api,
        metadata_api=metadata_api,
    )
    binder.bind(TimelineService, timeline_service)


def get_database() -> Database:
    return inject.instance(Database)


def get_timeline_service() -> TimelineService:
    return inject.instance(TimelineService)


if not inject.is_configured():
    inject.configure(container_config)
