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
    POSTGRES_SUPERUSERNAME: str
    POSTGRES_SUPERUSERPASS: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_SUPERUSERDB: str
    DATABASE_URL: PostgresDsn = None
    DATABASE_TABLE_PREFIX: str = "saasr_"

    # initial data
    SAASR_SUPERUSER_EMAIL: str
    SAASR_SUPERUSER_PASSWORD: str
    MAIL_SENDER_EMAIL: str = "oguz@example.com"
    MAIL_SENDER_NAME: str = "Oğuz Altun"

    # mail
    SENDINBLUE_API_KEY: str

    # iyzico
    IYZICO_API_KEY: str
    IYZICO_SECRET_KEY: str
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
    settings.DATABASE_URL = f"postgresql://{settings.POSTGRES_SUPERUSERNAME}:{settings.POSTGRES_SUPERUSERPASS}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_SUPERUSERDB}"

if settings.SAASR_DEBUG:
    print("SETTINGS", settings)
