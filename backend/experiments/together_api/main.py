"""
main.py
-------
Entry point: legge input.json, chiama TogetherLib e scrive output.json.

Uso:
    python main.py
    python main.py --input my_input.json --output my_output.json
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from together_lib import TogetherLib, DEFAULT_MODEL

# ---------------------------------------------------------------------------
# Configurazione del caso d'uso — modifica qui prompt e schema
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """
Sei un assistente esperto in geografia e cultura generale.
Rispondi SEMPRE e SOLO con un oggetto JSON valido, senza testo aggiuntivo.
Rispetta scrupolosamente lo schema JSON fornito nella richiesta utente.
""".strip()

OUTPUT_SCHEMA = {
    "answer": "risposta alla domanda",
    "explanation": "spiegazione dettagliata della risposta",
    "confidence": "livello di confidenza da 0.0 a 1.0",
    "language": "codice lingua ISO 639-1 usato nella risposta (es. 'it', 'en')",
    "sources_hint": "eventuali fonti o riferimenti utili (stringa, può essere vuota)",
}

MODEL = DEFAULT_MODEL


# ---------------------------------------------------------------------------
# Formato del file output.json
# ---------------------------------------------------------------------------

def build_output(
    input_data: dict,
    result: dict,
    status: str = "success",
    error: str | None = None,
) -> dict:
    return {
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "model": MODEL,
        },
        "input": input_data,
        "result": result,
        "error": error,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Chiama Together AI su un file JSON di input.")
    parser.add_argument(
        "--input", "-i",
        default="input.json",
        help="Percorso del file JSON di input (default: input.json)",
    )
    parser.add_argument(
        "--output", "-o",
        default="output.json",
        help="Percorso del file JSON di output (default: output.json)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    # --- Lettura input ---
    if not input_path.exists():
        print(f"[ERRORE] File di input non trovato: {input_path}", file=sys.stderr)
        sys.exit(1)

    with input_path.open(encoding="utf-8") as f:
        input_data: dict = json.load(f)

    print(f"[OK] Input letto da: {input_path}")
    print(f"     Contenuto: {json.dumps(input_data, ensure_ascii=False)}")

    # --- Chiamata Together AI ---
    lib = TogetherLib(
        system_prompt=SYSTEM_PROMPT,
        output_schema=OUTPUT_SCHEMA,
        model=MODEL,
    )

    status = "success"
    result: dict = {}
    error_msg: str | None = None

    try:
        result = lib.run(input_data)
        print(f"[OK] Risposta ricevuta dal modello.")
    except (ValueError, RuntimeError) as exc:
        status = "error"
        error_msg = str(exc)
        print(f"[ERRORE] {error_msg}", file=sys.stderr)

    # --- Scrittura output ---
    output = build_output(input_data, result, status, error_msg)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"[OK] Output scritto in: {output_path}")

    if status == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
