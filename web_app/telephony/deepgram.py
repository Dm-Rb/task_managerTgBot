import asyncio
import mimetypes
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import httpx


class DeepgramError(Exception):
    """Ошибка при обращении к Deepgram API."""


@dataclass
class Turn:
    speaker: int | None   # None, если diarize выключен
    start: float          # секунды
    end: float
    text: str


@dataclass
class TranscriptionResult:
    text: str                                   # весь текст сплошным полотном
    dialogue: str                               # готовый диалог с таймкодами и спикерами
    turns: list[Turn] = field(default_factory=list)                  # склеенные реплики
    utterances: list[dict[str, Any]] = field(default_factory=list)   # исходные куски Deepgram
    raw: dict[str, Any] = field(default_factory=dict)                # сырой ответ


class DeepgramClient:
    # Настройки распознавания ---
    MODEL: str = "nova-3"
    LANGUAGE: str = "ru"
    SPEAKER_LABEL: str = "Собеседник"
    SPEAKER_NUMBER_OFFSET: int = 1   # Deepgram нумерует с 0; 1 даёт «Собеседник 1», «Собеседник 2»
    MERGE_MAX_PAUSE: float | None = None   # None = склеивать всегда; число = не склеивать при паузе дольше N секунд
    SMART_FORMAT: bool = True
    DIARIZE: bool = True
    UTTERANCES: bool = True

    # Настройки соединения ---
    BASE_URL: str = "https://api.deepgram.com/v1"
    REQUEST_TIMEOUT: float = 30.0        # обычные запросы (баланс и т.п.)
    TRANSCRIBE_TIMEOUT: float = 600.0    # распознавание длинных файлов
    DEFAULT_CONTENT_TYPE: str = "application/octet-stream"

    def __init__(self, token: str) -> None:
        if not token:
            raise ValueError("Токен Deepgram не задан")
        self._token = token
        self._project_id: str | None = None

    async def get_balance(self) -> dict[str, Any]:
        """Возвращает суммарный баланс проекта: {"amount": float, "units": str}."""
        project_id = await self._get_project_id()
        data = await self._request("GET", f"/projects/{project_id}/balances")

        balances = data.get("balances", [])
        total = sum(float(b.get("amount", 0)) for b in balances)
        units = balances[0].get("units", "usd") if balances else "usd"
        return {"amount": total, "units": units}

    async def transcribe_file(self, file_path: str | Path) -> TranscriptionResult:
        """Отправляет на распознавание файл с диска."""
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Файл не найден: {path}")

        # чтение файла в отдельном потоке, чтобы не блокировать event loop
        audio = await asyncio.to_thread(path.read_bytes)
        content_type = self._guess_content_type(path.name)
        return await self.transcribe_bytes(audio, content_type)
    

    async def transcribe_bytes(
        self, audio: bytes, content_type: str | None = None
    ) -> TranscriptionResult:
        """Отправляет на распознавание аудио, уже лежащее в памяти."""
        if not audio:
            raise ValueError("Пустые аудиоданные")

        data = await self._request(
            "POST",
            "/listen",
            params=self._build_params(),
            headers={"Content-Type": content_type or self.DEFAULT_CONTENT_TYPE},
            content=audio,
            timeout=self.TRANSCRIBE_TIMEOUT,
        )
        return self._parse_result(data)

    def _build_params(self) -> dict[str, str]:
        return {
            "model": self.MODEL,
            "language": self.LANGUAGE,
            "smart_format": self._bool(self.SMART_FORMAT),
            "diarize": self._bool(self.DIARIZE),
            "utterances": self._bool(self.UTTERANCES),
        }

    @staticmethod
    def _bool(value: bool) -> str:
        return "true" if value else "false"

    @staticmethod
    def _guess_content_type(filename: str) -> str:
        return mimetypes.guess_type(filename)[0] or DeepgramClient.DEFAULT_CONTENT_TYPE

    async def _get_project_id(self) -> str:
        """ID проекта нужен для запроса баланса. Запрашивается один раз и кэшируется."""
        if self._project_id is None:
            data = await self._request("GET", "/projects")
            projects = data.get("projects", [])
            if not projects:
                raise DeepgramError("У токена нет доступных проектов")
            self._project_id = projects[0]["project_id"]
        return self._project_id

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        content: bytes | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        all_headers = {"Authorization": f"Token {self._token}"}
        if headers:
            all_headers.update(headers)

        try:
            async with httpx.AsyncClient(
                base_url=self.BASE_URL,
                timeout=httpx.Timeout(timeout or self.REQUEST_TIMEOUT),
            ) as client:
                response = await client.request(
                    method, path, params=params, headers=all_headers, content=content
                )
        except httpx.HTTPError as e:
            raise DeepgramError(f"Сетевая ошибка: {e!r}") from e

        if response.is_error:
            raise DeepgramError(f"Deepgram {response.status_code}: {response.text}")
        return response.json()

    ###
    def _parse_result(self, data: dict[str, Any]) -> TranscriptionResult:
            results = data.get("results", {})
            utterances = results.get("utterances") or []

            try:
                text = results["channels"][0]["alternatives"][0]["transcript"]
            except (KeyError, IndexError):
                text = " ".join(u.get("transcript", "") for u in utterances)

            turns = self._build_turns(utterances)
            return TranscriptionResult(
                text=text,
                dialogue=self._format_dialogue(turns) or text,
                turns=turns,
                utterances=utterances,
                raw=data,
            )

    def _build_turns(self, utterances: list[dict[str, Any]]) -> list[Turn]:
        """Склеивает подряд идущие реплики одного спикера."""
        turns: list[Turn] = []
        for u in utterances:
            piece = (u.get("transcript") or "").strip()
            if not piece:
                continue

            speaker = u.get("speaker")
            start = float(u.get("start", 0))
            end = float(u.get("end", 0))

            last = turns[-1] if turns else None
            if last and last.speaker == speaker and self._pause_allows_merge(last.end, start):
                last.text += " " + piece
                last.end = max(last.end, end)
            else:
                turns.append(Turn(speaker=speaker, start=start, end=end, text=piece))
        return turns

    def _pause_allows_merge(self, prev_end: float, next_start: float) -> bool:
        if self.MERGE_MAX_PAUSE is None:
            return True
        return next_start - prev_end <= self.MERGE_MAX_PAUSE

    def _format_dialogue(self, turns: list[Turn]) -> str:
        lines = []
        for t in turns:
            if t.speaker is not None:
                label = f"{self.SPEAKER_LABEL} {t.speaker + self.SPEAKER_NUMBER_OFFSET}: "
            else:
                label = ""
            lines.append(f"[{self._format_time(t.start)}] {label}{t.text}")
        return "\n".join(lines)

    @staticmethod
    def _format_time(seconds: float) -> str:
        hours, rest = divmod(int(seconds), 3600)
        minutes, secs = divmod(rest, 60)
        return f"{hours}:{minutes:02d}:{secs:02d}" if hours else f"{minutes:02d}:{secs:02d}"
    
    
