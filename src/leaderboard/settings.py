from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    azure_client_id: str
    azure_tenant_id: str
    # Pre-fill these after first run to skip interactive selection
    teams_team_id: str = ""
    teams_channel_id: str = ""
    challenge_message_id: str = ""
