import datetime
import logging
import re
from core.config import settings
from database.repositories.call_logs import CallRepository

from .deepgram import DeepgramClient
from .gemini import GeminiClient

logger = logging.getLogger(__name__)


class TelephonyService:

    def __init__(self, calllogs_database: CallRepository):
        self.deepgram = DeepgramClient(settings.DEEPGRAM_TOKEN)
        self.gemini = GeminiClient(settings.GEMINI_TOKEN)
        self.calllogs_database = calllogs_database

    async def transcribe_call(self, audio: bytes, file_name: str | None) -> None:
        try:
            transcribe = await self.deepgram.transcribe_bytes(audio)
        except Exception:
            logger.exception("Ошибка распознавания для %s", file_name)
            return
        transcribe_text = transcribe.dialogue
        from_ = self._extract_phone(file_name)
        datetime_ = self._extract_datetime(file_name)
        short_text = None
        call_database = await self.calllogs_database.create(
            from_=from_,
            short_text=short_text,
            text=transcribe_text,
            completed_at=datetime_,
        )
        if transcribe_text.strip():
            try:
                short_text = await self.gemini.analyze_text(transcribe_text)
                await self.calllogs_database.update_by_id(
                    call_id=call_database.id,
                    short_text=short_text,
                )
            except Exception:
                logger.exception("Не удалось получить краткое содержание для %s", file_name)
        else:
            logger.warning("Пустая расшифровка для %s, анализ пропущен", file_name)


        
    async def get_balance_deepgram(self) -> str:
        r = await self.deepgram.get_balance()
        return f"{r['amount']:.2f} {r['units']}"
    
    @staticmethod
    def _extract_phone(text: str | None) -> str | None:
        if not text:
            return None
        match = re.search(r"\((\d+)\)", text)
        if not match:
            return None
        return re.sub(r"^00", "+", match.group(1))
    
    @staticmethod
    def _extract_datetime(text: str | None) -> str | None:
        match = re.search(r'\)_(\d{14})', text)
        if not match:
            return None
        return datetime.datetime.strptime(match.group(1), "%Y%m%d%H%M%S")
    
    def get_prompt(self):
        try:
            return self.gemini.system_prompt
        except Exception as ex:
            return str(ex)
    
    async def update_system_prompt(self, text: str):
        await self.gemini.update_system_prompt(text)
    
    