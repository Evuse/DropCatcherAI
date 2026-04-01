import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.paths import get_env_path, get_db_path, get_downloads_dir

class Settings(BaseSettings):
    APP_NAME: str = "DropCatcher"
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000
    DATABASE_URL: str = f"sqlite:///{get_db_path()}"
    DEFAULT_AUTO_START_WINDOW_SECONDS: int = 60
    NICIT_BASE_URL: str = "https://www.nic.it/droptime/files"
    NICIT_DOWNLOAD_DIR: str = get_downloads_dir()

    DYNADOT_ENABLED: bool = False
    DYNADOT_API_KEY: str = ""
    DYNADOT_API_SECRET: str = ""
    DYNADOT_IT_CONTACT_CONFIRMED: bool = False
    DYNADOT_IT_CONTACT_COUNTRY_CODE: str = "IT"
    DYNADOT_IT_CONTACT_PROVINCE_CODE: str = "MI"

    OPENPROVIDER_ENABLED: bool = False
    OPENPROVIDER_API_TOKEN: str = ""
    OPENPROVIDER_OWNER_HANDLE: str = ""
    OPENPROVIDER_ADMIN_HANDLE: str = ""
    OPENPROVIDER_TECH_HANDLE: str = ""
    OPENPROVIDER_BILLING_HANDLE: str = ""
    OPENPROVIDER_NAMESERVER_GROUP: str = ""
    OPENPROVIDER_IT_CONTACTS_VERIFIED: bool = False
    OPENPROVIDER_IT_ADDITIONAL_DATA_JSON: str = "{}"

    model_config = SettingsConfigDict(
        env_file=get_env_path(), 
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()
