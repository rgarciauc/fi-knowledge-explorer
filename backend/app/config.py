from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    neo4j_uri: str = "neo4j://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "SuperBank_ChangeMe_2026"

    llm_enabled: bool = True
    llm_url: str = "http://localhost:11434/api/generate"
    llm_model: str = "llama3.2:3b"
    llm_timeout_seconds: float = 120.0

    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")


settings = Settings()
