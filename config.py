from pydantic import BaseSettings

# loading the dotenv


class Setting(BaseSettings):
    HOST: str
    PORT: int
    ALGORITHM: str
    PRIVATE_KEY: str
    PUBLIC_KEY: str
    DATABASE_URL: str
    UPLOAD_FOLDER: str

    class Config:
        env_file = ".env"


# initiating the settings object
setting = Setting()
