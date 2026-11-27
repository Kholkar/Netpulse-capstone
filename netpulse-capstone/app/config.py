import os
from dataclasses import dataclass
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    persistence_backend: str = os.getenv("PERSISTENCE_BACKEND", "memory").lower()
    mysql_host: str = os.getenv("MYSQL_HOST", "localhost")
    mysql_port: int = int(os.getenv("MYSQL_PORT", "3306"))
    mysql_db: str = os.getenv("MYSQL_DB", "netpulse_db")
    mysql_user: str = os.getenv("MYSQL_USER", "netpulse_user")
    mysql_password: str = os.getenv("MYSQL_PASSWORD", "change_me")

    @property
    def database_url(self) -> str:
        explicit_url = os.getenv("DATABASE_URL")
        if explicit_url:
            return explicit_url

        user = quote_plus(self.mysql_user)
        password = quote_plus(self.mysql_password)
        return (
            f"mysql+pymysql://{user}:{password}@{self.mysql_host}:"
            f"{self.mysql_port}/{self.mysql_db}"
        )


settings = Settings()