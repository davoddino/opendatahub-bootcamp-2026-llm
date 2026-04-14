"""
together_lib.py
---------------
Libreria riutilizzabile per chiamate a Together AI.
"""

from __future__ import annotations

import json
import os
import ssl
from pathlib import Path
from typing import Any
from urllib import request, error

import certifi
from dotenv import load_dotenv


DEFAULT_SYSTEM_PROMPT = """
Sei un assistente esperto. Rispondi SEMPRE e SOLO con un oggetto JSON valido,
senza testo aggiuntivo prima o dopo.
Rispetta scrupolosamente lo schema JSON fornito nella richiesta utente.
""".strip()

DEFAULT_OUTPUT_SCHEMA: dict[str, Any] = {
    "rating": "intero da 0 a 10",
    "response": "feedback per l'utente",
    "ingredientsMap": [],
}

DEFAULT_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"


class TogetherLib:
    """
    Wrapper attorno a Together AI che:
    - accetta un dict JSON in input
    - forza un output JSON con schema definito
    - restituisce un dict JSON
    """

    def __init__(
        self,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        output_schema: dict[str, Any] = DEFAULT_OUTPUT_SCHEMA,
        model: str = DEFAULT_MODEL,
        env_path: Path | None = None,
    ) -> None:
        self.system_prompt = system_prompt
        self.output_schema = output_schema
        self.model = model
        self._load_env(env_path)
        api_key = os.environ.get("TOGETHER_API_KEY")
        if not api_key:
            raise RuntimeError(
                "TOGETHER_API_KEY non trovata. Impostala nel file .env o come variabile d'ambiente."
            )
        self.api_key = api_key

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Invia input_data al modello e restituisce un dict con il risultato."""
        user_message = self._build_user_message(input_data)

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message},
            ],
            "response_format": {"type": "json_object"},
        }

        req = request.Request(
            url="https://api.together.xyz/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            with request.urlopen(req, timeout=90, context=ssl_context) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="ignore") if exc.fp else ""
            raise RuntimeError(f"Together API HTTP error {exc.code}: {error_body}") from exc
        except error.URLError as exc:
            raise RuntimeError(f"Together API network error: {exc.reason}") from exc

        try:
            raw_content = response_payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError(f"Unexpected Together response format: {response_payload}") from exc

        return self._parse_json(raw_content)

    def _build_user_message(self, input_data: dict[str, Any]) -> str:
        """Costruisce il messaggio utente includendo i dati di input e lo schema atteso."""
        schema_str = json.dumps(self.output_schema, ensure_ascii=False, indent=2)
        input_str = json.dumps(input_data, ensure_ascii=False, indent=2)
        return (
            f"## Input\n{input_str}\n\n"
            f"## Schema di output atteso\n"
            f"Restituisci un oggetto JSON con esattamente questi campi:\n{schema_str}"
        )

    @staticmethod
    def _parse_json(raw: str) -> dict[str, Any]:
        """Prova a decodificare il JSON restituito dal modello."""
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Il modello non ha restituito JSON valido.\nRisposta raw:\n{raw}"
            ) from exc
        if not isinstance(parsed, dict):
            raise ValueError(
                f"Il modello non ha restituito un oggetto JSON valido.\nRisposta raw:\n{raw}"
            )
        return parsed

    @staticmethod
    def _load_env(env_path: Path | None) -> None:
        """Carica .env: prima il path esplicito, poi i parent noti fino alla root repo."""
        if env_path:
            load_dotenv(env_path)
            return
        script_dir = Path(__file__).resolve().parent
        load_dotenv(script_dir / ".env")
        load_dotenv(script_dir.parent / ".env")
        load_dotenv(script_dir.parent.parent / ".env")
        load_dotenv(script_dir.parent.parent.parent / ".env")
