import os
from dotenv import load_dotenv


"""Load environment variables from .env"""


load_dotenv()


class Config:
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    ADMIN_PSW = os.getenv("ADMIN_PASSWORD")
    USER_PSW = os.getenv("USER_PASSWORD")
    MAX_ATTS_PSW = int(os.getenv("MAX_ATTEMPTS_PASSWORD"))
    DATABASE_URL = os.getenv("DATABASE_URL")

settings = Config()