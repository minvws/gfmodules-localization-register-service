
import inject

from app.api.addressing.api import AddressingApi
from app.api.localisation.api import LocalisationApi
from app.api.metadata.api import MetadataApi
from app.timeline.timeline_service import TimelineService
from app.config import get_config


def container_config(binder: inject.Binder) -> None:
    config = get_config()

    cfg = config.localisation_api
    localisation_api = LocalisationApi(
        endpoint=cfg.endpoint,
        timeout=cfg.timeout,
        mtls_cert=cfg.mtls_cert if cfg.mtls_cert else "",
        mtls_key=cfg.mtls_key if cfg.mtls_key else "",
        mtls_ca=cfg.mtls_ca if cfg.mtls_ca else ""
    )

    cfg = config.addressing_api  # type: ignore
    addressing_api = AddressingApi(
        endpoint=cfg.endpoint,
        timeout=cfg.timeout,
        mtls_cert=cfg.mtls_cert if cfg.mtls_cert else "",
        mtls_key=cfg.mtls_key if cfg.mtls_key else "",
        mtls_ca=cfg.mtls_ca if cfg.mtls_ca else ""
    )

    cfg = config.metadata_api  # type: ignore
    metadata_api = MetadataApi(
        timeout=cfg.timeout,
        mtls_cert=cfg.mtls_cert if cfg.mtls_cert else "",
        mtls_key=cfg.mtls_key if cfg.mtls_key else "",
        mtls_ca=cfg.mtls_ca if cfg.mtls_ca else ""
    )

    timeline_service = TimelineService(
        localisation_api=localisation_api,
        addressing_api=addressing_api,
        metadata_api=metadata_api,
    )
    binder.bind(TimelineService, timeline_service)

def get_timeline_service() -> TimelineService:
    return inject.instance(TimelineService)


if not inject.is_configured():
    inject.configure(container_config)
