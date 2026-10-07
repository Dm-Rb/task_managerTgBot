import os
from dotenv import load_dotenv


"""Load environment variables from .env"""


load_dotenv()


class Config:
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    LOGIN_WEB = os.getenv("LOGIN_WEB")
    ADMIN_PSW = os.getenv("ADMIN_PASSWORD")
    USER_PSW = os.getenv("USER_PASSWORD")
    MAX_ATTS_PSW = int(os.getenv("MAX_ATTEMPTS_PASSWORD"))
    DATABASE_URL = os.getenv("DATABASE_URL")
    HOST = os.getenv("HOST")
    PORT = os.getenv("PORT")
    PUBLIC_IP=os.getenv("PUBLIC_IP")
    WEBHOOK_KEY=os.getenv("WEBHOOK_KEY")
    DEEPGRAM_TOKEN=os.getenv("DEEPGRAM_TOKEN")
    GEMINI_TOKEN=os.getenv("GEMINI_TOKEN")
    
settings = Config()
