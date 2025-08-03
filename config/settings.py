from pydantic.v1 import Field, BaseSettings


class Settings(BaseSettings):
    BASE_URL: str = Field(default="https://rostender.info", env="BASE_URL")
    COUNT_TENDERS: int = Field(default=100, env='COUNT_TENDERS')
    USER_AGENT: str = Field(
        default="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        env="USER_AGENT"
    )
    OUTPUT_FILE: str = Field(default="tenders.csv", env="OUTPUT_FILE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
