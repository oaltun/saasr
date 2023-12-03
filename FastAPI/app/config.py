from pydantic import BaseSettings, PostgresDsn, SecretStr
import os


class InitialSettings(BaseSettings):
    secrets_dir = "/run/secrets"

    class Config:
        case_sensitive = False
        env_file = ".env", "../.env/share.env"
        env_file_encoding = "utf-8"


initial_settings = InitialSettings()


class AppSettings(BaseSettings):
    class Config:
        secrets_dir = initial_settings.secrets_dir
        case_sensitive = False
        env_file = ".env", "../.env/share.env"
        env_file_encoding = "utf-8"

    # db
    SHAREDPOSTGRES_SUPERUSERNAME: str
    SHAREDPOSTGRES_SUPERUSERPASS: str
    SHAREDPOSTGRES_HOST: str
    SHAREDPOSTGRES_PORT: int
    SHAREDPOSTGRES_SUPERUSERDB: str
    DATABASE_URL: PostgresDsn = None
    DATABASE_TABLE_PREFIX: str = "saasr_"

    # initial data
    SAASR_SUPERUSER_EMAIL: str
    SAASR_SUPERUSER_PASSWORD: str
    MAIL_SENDER_EMAIL: str = "oguz@example.com"
    MAIL_SENDER_NAME: str = "Oğuz Altun"

    # mail
    SAASR_SENDINBLUE_API_KEY: str

    # iyzico
    SAASR_IYZICO_API_KEY: str
    SAASR_IYZICO_SECRET_KEY: str
    IYZICO_BASE_URL: str = "sandbox-api.iyzipay.com"

    # env
    SAASR_DEBUG: bool = False

    # Saasr specific
    # settings
    PASSWORD_RESET_VALID_FOR_HOURS: int = 1
    EMAIL_VERIFICATION_VALID_FOR_HOURS: int = 1

    PROJECT_NAME: str = "Exam Add-In"
    SAASR_TOKEN_ALGORITHM: str
    SAASR_TOKEN_SECRET_KEY: str
    TOKEN_EXPIRE_MINUTES = 240  # minutes


settings = AppSettings()
if settings.DATABASE_URL is None:
    settings.DATABASE_URL = f"postgresql://{settings.SHAREDPOSTGRES_SUPERUSERNAME}:{settings.SHAREDPOSTGRES_SUPERUSERPASS}@{settings.SHAREDPOSTGRES_HOST}:{settings.SHAREDPOSTGRES_PORT}/{settings.SHAREDPOSTGRES_SUPERUSERDB}"

if settings.SAASR_DEBUG:
    print("SETTINGS", settings)
