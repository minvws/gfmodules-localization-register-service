from app.config import Config, ConfigApp, LogLevel, ConfigUvicorn, ConfigTelemetry, \
    ConfigLocalisationApi, ConfigAddressingApi, ConfigMetadataApi, ConfigStats


def get_test_config() -> Config:
    return Config(
        app=ConfigApp(
            loglevel=LogLevel.error,
        ),
        localisation_api=ConfigLocalisationApi(
            endpoint="http://localisation-api",
            timeout=30,
        ),
        addressing_api=ConfigAddressingApi(
            endpoint="http://addressing-api",
            timeout=30,
        ),
        metadata_api=ConfigMetadataApi(
            timeout=30,
        ),
        uvicorn=ConfigUvicorn(
            swagger_enabled=False,
            docs_url="/docs",
            redoc_url="/redoc",
            host="0.0.0.0",
            port=8503,
            reload=True,
            use_ssl=False,
            ssl_base_dir=None,
            ssl_cert_file=None,
            ssl_key_file=None,
        ),
        telemetry=ConfigTelemetry(
            enabled=False,
            endpoint=None,
            service_name=None,
            tracer_name=None,
        ),
        stats=ConfigStats(
            enabled=False,
            host=None,
            port=None,
            module_name=None,
        ),
    )
