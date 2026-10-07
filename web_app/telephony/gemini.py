import asyncio
import json
from pathlib import Path
from typing import Any
import httpx
from pathlib import Path


class GeminiError(Exception):
    """Ошибка при обращении к Gemini API."""


class GeminiClient:
    # --- Настройки модели ---
    MODEL: str = "gemini-3.8-flash"
    TEMPERATURE: float = 0.3
    MAX_OUTPUT_TOKENS: int = 4000
    THINKING_BUDGET: int = 0   # 0 = без «размышлений», быстрее и дешевле; -1 = динамический режим

    # --- Настройки соединения ---
    BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta"
    CHAT_TIMEOUT: float = 180.0
    # --- Таймаут и повторы ---
    ATTEMPT_TIMEOUT: float = 200.0    # жёсткий лимит на одну попытку, сек
    RETRY_ATTEMPTS: int = 5          # всего попыток
    RETRY_BASE_DELAY: float = 2.0    # паузы между попытками: 2, 4, 8, 16 сек
    RETRY_STATUSES: tuple[int, ...] = (429, 500, 502, 503, 504)

    # --- Системный промпт ---
    PROMPT_PATH: Path = Path(__file__).resolve().parent / "system_prompt.json"
    PROMPT_KEY: str = "system_prompt"

    def __init__(self, token: str, prompt_path: str | Path | None = None) -> None:
        if not token:
            raise ValueError("Токен Gemini не задан")
        self._token = token
        self._prompt_path = Path(prompt_path or self.PROMPT_PATH)
        self._system_prompt: str | None = None

    # ===================== Публичные методы =====================

    async def analyze_text(self, text: str) -> str:
        """Отправляет текст на анализ с системным промптом из JSON-файла, возвращает ответ модели."""
        if not text or not text.strip():
            raise ValueError("Пустой текст для анализа")

        system_prompt = await self._get_system_prompt()
        payload = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": text}]}],
            "generationConfig": {
                "temperature": self.TEMPERATURE,
                "maxOutputTokens": self.MAX_OUTPUT_TOKENS,
                "thinkingConfig": {"thinkingBudget": self.THINKING_BUDGET},
            },
        }
        data = await self._request(
            "POST", f"/models/{self.MODEL}:generateContent", json_body=payload
        )
        return self._extract_text(data)

    # ===================== Приватные методы =====================

    @staticmethod
    def _extract_text(data: dict[str, Any]) -> str:
        """Достаёт текст ответа и проверяет, что запрос не был заблокирован или обрезан."""
        block_reason = data.get("promptFeedback", {}).get("blockReason")
        if block_reason:
            raise GeminiError(f"Запрос заблокирован: {block_reason}")

        candidates = data.get("candidates") or []
        if not candidates:
            raise GeminiError(f"Пустой ответ модели: {data}")

        candidate = candidates[0]
        parts = candidate.get("content", {}).get("parts") or []
        text = "".join(p.get("text", "") for p in parts if not p.get("thought")).strip()

        if not text:
            raise GeminiError(
                f"Модель не вернула текст (finishReason={candidate.get('finishReason')})"
            )
        return text

    async def _get_system_prompt(self) -> str:
        """Читает промпт из JSON-файла (при первом обращении) и кэширует."""
        if self._system_prompt is None:
            self._system_prompt = await asyncio.to_thread(self._load_system_prompt)
        return self._system_prompt

    def _load_system_prompt(self) -> str:
        if not self._prompt_path.is_file():
            raise FileNotFoundError(f"Файл с промптом не найден: {self._prompt_path}")
        try:
            data = json.loads(self._prompt_path.read_text(encoding="utf-8"))
            prompt = data[self.PROMPT_KEY]
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            raise GeminiError(
                f"В {self._prompt_path} нужен JSON-объект с ключом '{self.PROMPT_KEY}'"
            ) from e
        if not isinstance(prompt, str) or not prompt.strip():
            raise GeminiError("Системный промпт пустой или не строка")
        return prompt

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        headers = {"x-goog-api-key": self._token}
        last_error: GeminiError | None = None

        for attempt in range(1, self.RETRY_ATTEMPTS + 1):
            if attempt > 1:
                await asyncio.sleep(self.RETRY_BASE_DELAY * 2 ** (attempt - 2))

            try:
                # жёсткий общий лимит на попытку: по истечении запрос отменяется,
                # а выход из async with закрывает соединение
                async with asyncio.timeout(self.ATTEMPT_TIMEOUT):
                    async with httpx.AsyncClient(
                        base_url=self.BASE_URL,
                        timeout=httpx.Timeout(self.ATTEMPT_TIMEOUT),
                    ) as client:
                        response = await client.request(
                            method, path, headers=headers, json=json_body
                        )
            except TimeoutError:
                last_error = GeminiError(f"Таймаут {self.ATTEMPT_TIMEOUT} с")
            except httpx.HTTPError as e:
                last_error = GeminiError(f"Сетевая ошибка: {e!r}")
            else:
                if response.status_code in self.RETRY_STATUSES:
                    last_error = GeminiError(f"Gemini {response.status_code}: {response.text}")
                elif response.is_error:
                    # 400, 401, 403, 404 и т.п.: повтор не поможет
                    raise GeminiError(f"Gemini {response.status_code}: {response.text}")
                else:
                    return response.json()

        raise GeminiError(
            f"Все {self.RETRY_ATTEMPTS} попыток исчерпаны, последняя ошибка: {last_error}"
        )