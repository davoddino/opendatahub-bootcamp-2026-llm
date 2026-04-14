"""
main.py
-------
CLI sperimentale: legge input.json, invoca la logica riusabile in backend/src/llm
e scrive output.json.

Uso:
    python main.py
    python main.py --input my_input.json --output my_output.json
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from backend.src.llm.llm_logic import process_input_file

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

    try:
        process_input_file(input_path, output_path)
        print(f"[OK] Input letto da: {input_path}")
        print(f"[OK] Output scritto in: {output_path}")
    except FileNotFoundError as exc:
        print(f"[ERRORE] {exc}", file=sys.stderr)
        sys.exit(1)
    except (ValueError, RuntimeError) as exc:
        print(f"[ERRORE] {exc}", file=sys.stderr)
        print(f"[OK] Output scritto in: {output_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
