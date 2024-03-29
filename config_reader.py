from pydantic_settings import BaseSettings
from pydantic import SecretStr


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    namesColumn: str
    datesColumn: str
    daysLeft: int
   
    class Config:
        env_file = '.cfg'
        env_file_encoding = 'utf-8'
        
config = Settings()
