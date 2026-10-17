from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config =SettingsConfigDict(env_file=".env", extra="ignore")
    # shared secret the ci workflow sends when uploading reports
    ingest_token: str = ""

    # defaults are empty so tests can import the app without a real env file
    database_url: str = ""
    hackclub_api_key: str = ""
    hackclub_base_url: str = "https://ai.hackclub.com/proxy/v1"
    llm_model: str = "deepseek/deepseek-chat"
    embedding_model: str = ""
    


settings = Settings()