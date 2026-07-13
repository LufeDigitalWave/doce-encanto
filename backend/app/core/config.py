"""Application configuration loaded from environment variables.

Settings are read once at startup. The `DEMO_MODE` flag selects which
provider implementations are wired in `core.deps` — the rest of the
codebase must not branch on it.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Mode ----------------------------------------------------------------
    demo_mode: bool = Field(default=True, alias="DEMO_MODE")

    # Database ------------------------------------------------------------
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@db:5432/doce_encanto",
        alias="DATABASE_URL",
    )

    # Admin ---------------------------------------------------------------
    admin_username: str = Field(default="admin", alias="ADMIN_USERNAME")
    admin_password: str = Field(default="demo1234", alias="ADMIN_PASSWORD")
    jwt_secret: str = Field(default="change-me", alias="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    jwt_ttl_minutes: int = 60 * 12  # 12h

    # AbacatePay ----------------------------------------------------------
    abacatepay_api_key: str = Field(default="", alias="ABACATEPAY_API_KEY")
    abacatepay_webhook_secret: str = Field(default="", alias="ABACATEPAY_WEBHOOK_SECRET")
    public_base_url: str = Field(default="http://localhost:8000", alias="PUBLIC_BASE_URL")

    # Resend --------------------------------------------------------------
    resend_api_key: str = Field(default="", alias="RESEND_API_KEY")
    email_from: str = Field(default="pedidos@doceencanto.demo", alias="EMAIL_FROM")

    # Scheduling ----------------------------------------------------------
    min_lead_time_hours: int = Field(default=24, alias="MIN_LEAD_TIME_HOURS")
    slot_capacity: int = Field(default=5, alias="SLOT_CAPACITY")
    days_ahead: int = Field(default=14, alias="DAYS_AHEAD")

    # ---------------------------------------------------------------------
    @model_validator(mode="after")
    def _enforce_real_mode_credentials(self) -> "Settings":
        """If DEMO_MODE is off, the real provider credentials are mandatory."""
        if self.demo_mode:
            return self
        missing: list[str] = []
        if not self.abacatepay_api_key:
            missing.append("ABACATEPAY_API_KEY")
        if not self.abacatepay_webhook_secret:
            missing.append("ABACATEPAY_WEBHOOK_SECRET")
        # Resend is optional — if not set, emails fall back to console logs.
        # Only AbacatePay keys are strictly required for real Pix payments.
        if missing:
            raise RuntimeError(
                "DEMO_MODE=false requires these env vars to be set: "
                + ", ".join(missing)
                + ". Either set them or flip DEMO_MODE=true."
            )
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


# Convenient module-level access so tests can monkeypatch without DI gymnastics.
def reset_settings_cache() -> None:
    get_settings.cache_clear()


settings: Literal["singleton"] = "singleton"  # placeholder to silence linters
