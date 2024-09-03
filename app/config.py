import configparser
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ValidationError, Field

_PATH = "app.conf"
_CONFIG = None


class LogLevel(str, Enum):
    debug = "debug"
    info = "info"
    warning = "warning"
    error = "error"
    critical = "critical"


class ConfigApp(BaseModel):
    loglevel: LogLevel = Field(default=LogLevel.info)


class ConfigLocalisationApi(BaseModel):
    endpoint: str
    timeout: int = Field(default=30, gt=0)
    mtls_cert: Optional[str] = None
    mtls_key: Optional[str] = None
    mtls_ca: Optional[str] = None


class ConfigAddressingApi(BaseModel):
    endpoint: str
    timeout: int = Field(default=30, gt=0)
    mtls_cert: Optional[str] = None
    mtls_key: Optional[str] = None
    mtls_ca: Optional[str] = None


class ConfigMetadataApi(BaseModel):
    timeout: int = Field(default=30, gt=0)
    mtls_cert: Optional[str] = None
    mtls_key: Optional[str] = None
    mtls_ca: Optional[str] = None


class ConfigUvicorn(BaseModel):
    swagger_enabled: bool = Field(default=False)
    docs_url: str = Field(default="/docs")
    redoc_url: str = Field(default="/redoc")
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8505, gt=0, lt=65535)
    reload: bool = Field(default=True)
    reload_delay: float = Field(default=1)
    reload_dirs: list[str] = Field(default=["app"])
    use_ssl: bool = Field(default=False)
    ssl_base_dir: str | None
    ssl_cert_file: str | None
    ssl_key_file: str | None


class ConfigStats(BaseModel):
    enabled: bool = Field(default=False)
    host: str | None
    port: int | None
    module_name: str | None


class ConfigTelemetry(BaseModel):
    enabled: bool = Field(default=False)
    endpoint: str | None
    service_name: str | None
    tracer_name: str | None


class Config(BaseModel):
    app: ConfigApp
    uvicorn: ConfigUvicorn
    localisation_api: ConfigLocalisationApi
    addressing_api: ConfigAddressingApi
    metadata_api: ConfigMetadataApi
    telemetry: ConfigTelemetry
    stats: ConfigStats


def read_ini_file(path: str) -> Any:
    ini_data = configparser.ConfigParser()
    ini_data.read(path)

    ret = {}
    for section in ini_data.sections():
        ret[section] = dict(ini_data[section])

    return ret


def reset_config() -> None:
    global _CONFIG
    _CONFIG = None


def get_config(path: str | None = None) -> Config:
    global _CONFIG
    global _PATH

    if _CONFIG is not None:
        return _CONFIG

    if path is None:
        path = _PATH

    # To be inline with other python code, we use INI-type files for configuration. Since this isn't
    # a standard format for pydantic, we need to do some manual parsing first.
    ini_data = read_ini_file(path)

    try:
        _CONFIG = Config(**ini_data)
    except ValidationError as e:
        raise e

    return _CONFIG
