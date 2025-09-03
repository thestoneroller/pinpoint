from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, Literal, Annotated
from pydantic import AnyUrl, BeforeValidator, computed_field


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    """Settings for the application."""

    model_config = SettingsConfigDict(
        env_file="../../.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "Pinpoint"
    API_V1_STR: str = "/api/v1"

    GITHUB_TOKEN: str
    GOOGLE_API_KEY: str

    # OAuth App settings
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    SECRET_KEY: str

    FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = (
        []
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]


settings = Settings()
