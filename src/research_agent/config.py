import os 
from dotenv import load_dotenv 

load_dotenv()

class Settings:
    google_api_key: str = os.getenv("GOOGLE_API_KEY")
    model_name: str = os.getenv("MODEL_NAME", "gemini-2.5-flash")


settings = Settings()



def validate_settings() -> None:
    if not settings.google_api_key:
        raise ValueError("GOOGLE_API_KEY is not set in the environment variables.")