"""
together_lib.py
---------------
Libreria riutilizzabile per chiamate a Together AI.

Uso:
    lib = TogetherLib(
        system_prompt="Sei un assistente...",
        output_schema={
            "answer": "risposta alla domanda",
            "confidence": "livello di confidenza da 0 a 1",
            "language": "lingua della risposta (es. it, en)"
        },
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
    )
    result: dict = lib.run({"question": "Qual è la capitale d'Italia?"})
"""

import os
import json
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from together import Together


# ---------------------------------------------------------------------------
# Configurazione predefinita — personalizza qui il tuo caso d'uso
# ---------------------------------------------------------------------------

DEFAULT_SYSTEM_PROMPT = """
Sei un assistente esperto. Rispondi SEMPRE e SOLO con un oggetto JSON valido,
senza testo aggiuntivo prima o dopo.
Rispetta scrupolosamente lo schema JSON fornito nella richiesta utente.
""".strip()

DEFAULT_OUTPUT_SCHEMA: dict[str, str] = {
    "answer": "risposta alla domanda",
    "confidence": "livello di confidenza da 0.0 a 1.0",
    "language": "codice lingua ISO 639-1 (es. 'it', 'en')",
}

DEFAULT_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"


# ---------------------------------------------------------------------------
# Classe principale
# ---------------------------------------------------------------------------

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
        output_schema: dict[str, str] = DEFAULT_OUTPUT_SCHEMA,
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
        self.client = Together(api_key=api_key)

    # ------------------------------------------------------------------
    # Metodo pubblico
    # ------------------------------------------------------------------

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Invia input_data al modello e restituisce un dict con il risultato.

        Args:
            input_data: dizionario con i dati di input (viene serializzato in JSON).

        Returns:
            Dizionario con i campi definiti in output_schema.

        Raises:
            ValueError: se la risposta del modello non è JSON valido.
        """
        user_message = self._build_user_message(input_data)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message},
            ],
            response_format={"type": "json_object"},
        )

        raw_content = response.choices[0].message.content
        return self._parse_json(raw_content)

    # ------------------------------------------------------------------
    # Metodi privati
    # ------------------------------------------------------------------

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
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Il modello non ha restituito JSON valido.\nRisposta raw:\n{raw}"
            ) from exc

    @staticmethod
    def _load_env(env_path: Path | None) -> None:
        """Carica .env: prima il path esplicito, poi cartella script e parent noti fino alla root repo."""
        if env_path:
            load_dotenv(env_path)
            return
        script_dir = Path(__file__).resolve().parent
        load_dotenv(script_dir / ".env")
        load_dotenv(script_dir.parent / ".env")
        load_dotenv(script_dir.parent.parent / ".env")
        load_dotenv(script_dir.parent.parent.parent / ".env")
