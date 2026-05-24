from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    neo4j_uri: str = "neo4j://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "SuperBank_ChangeMe_2026"

    llm_enabled: bool = True
    llm_url: str = "http://localhost:11434/api/generate"
    llm_model: str = "llama3.2:3b"
    llm_timeout_seconds: float = 120.0
    ollama_keep_alive: str = "-1"
    entity_catalog_cache_seconds: float = 300.0

    intent_detection_enabled: bool = True
    global_search_enabled: bool = True
    generated_cypher_enabled: bool = True
    intent_confidence_threshold: float = 0.60
    entity_match_threshold: float = 0.70
    generated_query_timeout_seconds: float = 6.0
    generated_query_limit: int = 100
    expose_generated_cypher: bool = True

    log_level: str = "INFO"
    log_to_file: bool = True
    log_dir: str = "logs"

    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")


settings = Settings()
