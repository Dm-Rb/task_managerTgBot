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

    @staticmethod
    def _extract_phone(text: str | None) -> str | None:
        if not text:
            return None
        match = re.search(r"\((\d+)\)", text)
        if not match:
            return None
        return re.sub(r"^00", "+", match.group(1))

    async def transcribe_call(self, audio: bytes, file_name: str | None) -> None:
        try:
            transcribe = await self.deepgram.transcribe_bytes(audio)
        except Exception:
            logger.exception("Ошибка распознавания для %s", file_name)
            return
        transcribe_text = transcribe.dialogue

        short_text = None
        if transcribe_text.strip():
            try:
                short_text = await self.gemini.analyze_text(transcribe_text)
            except Exception:
                logger.exception("Не удалось получить краткое содержание для %s", file_name)
        else:
            logger.warning("Пустая расшифровка для %s, анализ пропущен", file_name)

        from_ = self._extract_phone(file_name)
        datetime_now = datetime.datetime.now().replace(second=0, microsecond=0)

        await self.calllogs_database.create(
            from_=from_,
            short_text=short_text,
            text=transcribe_text,
            completed_at=datetime_now,
        )
        
    async def get_balance_deepgram(self) -> str:
        r = await self.deepgram.get_balance()
        return f"{r['amount']:.2f} {r['units']}"
