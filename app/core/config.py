from pydantic_settings import BaseSettings, SettingsConfigDict
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=True
    )

    ENVIRONMENT: str
    HOST: str
    PORT: int

    SMTP_HOST: str
    SMTP_PORT: int
    FROM_EMAIL: str
    APP_PASSWORD: str


try:
    settings = Settings()
    logger.debug("Configuración cargada exitosamente")
    logger.debug(f"HOST: {settings.HOST}")
    logger.debug(f"PORT: {settings.PORT}")
    logger.debug(f"ENVIRONMENT: {settings.ENVIRONMENT}")

except Exception as e:
    logger.error(f"Error al cargar la configuración: {str(e)}")
    raise
