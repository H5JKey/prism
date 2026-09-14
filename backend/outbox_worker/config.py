from pathlib import Path
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    base_dir: Path = Path(__file__).parent
    base_delay_seconds: float = 1
    max_delay_seconds: float = 2 * 60

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        case_sensitive=False,
        env_file=base_dir / ".env",
        env_nested_delimiter="__",
    )


settings = Settings()
