from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    supabase_url: str = ""
    supabase_service_key: str = ""
    jwt_secret: str = "dev-secret-change-me"
    jwt_expire_hours: int = 72
    mapbox_token: str = ""
    gtfs_rt_url: str = ""
    upstash_redis_rest_url: str = ""
    upstash_redis_rest_token: str = ""
    cors_origins: str = "http://localhost:5173"
    admin_api_key: str = ""  # enables /api/admin/*; leave empty to disable


settings = Settings()
