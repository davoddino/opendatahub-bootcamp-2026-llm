"""
main.py
-------
Entry point: legge input.json, valuta gli ingredienti proposti dall'utente
con Together AI e scrive output.json.

Uso:
    python main.py
    python main.py --input my_input.json --output my_output.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from together_lib import TogetherLib, DEFAULT_MODEL

# ---------------------------------------------------------------------------
# Configurazione del caso d'uso — modifica qui prompt e schema
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """
Sei un assistente che valuta gli ingredienti indovinati da un utente
guardando soltanto l'immagine di una ricetta.

Rispondi SEMPRE e SOLO con un oggetto JSON valido, senza testo aggiuntivo.
Rispetta scrupolosamente lo schema JSON fornito nella richiesta utente.

Devi usare questi campi dell'input:
- `recipe.details.ingredients`: lista ufficiale degli ingredienti corretti
- `input`: risposta libera dell'utente con gli ingredienti che pensa di aver visto

Regole:
- ignora `output` se è presente nell'input
- confronta gli ingredienti proposti con quelli corretti in modo semantico, non solo testuale
- accetta ingredienti equivalenti o sufficientemente vicini, per esempio un ingrediente generico
  può andare bene se identifica chiaramente quello corretto
- `ingredientsMap` deve contenere una voce per ogni ingrediente corretto della ricetta
- `correctIngredient` deve riportare esattamente il testo presente nella ricetta
- `proposedIngredient` deve essere l'ingrediente dell'utente che meglio corrisponde, oppure `null`
- `accepted` è `true` solo se la proposta è accettabile per quell'ingrediente, altrimenti `false`
- `rating` deve essere un intero da 0 a 10
- `response` deve essere breve, utile e nella lingua della ricetta
""".strip()

OUTPUT_SCHEMA = {
    "rating": "intero da 0 a 10",
    "response": "breve feedback per l'utente nella lingua della ricetta dicendo anche quali ingredienti sono stati omessi. Se il rating è basso, spiega cosa è stato indovinato e cosa no.",
    "ingredientsMap": [
        {
            "correctIngredient": "ingrediente corretto preso da recipe.details.ingredients",
            "proposedIngredient": "ingrediente proposto dall'utente oppure null",
            "accepted": "booleano: true se accettato, false altrimenti",
        }
    ],
}

MODEL = DEFAULT_MODEL


# ---------------------------------------------------------------------------
# Validazione e formato del file output.json
# ---------------------------------------------------------------------------

def validate_input_data(input_data: dict[str, Any]) -> None:
    """Valida la struttura minima attesa dell'input."""
    recipe = input_data.get("recipe")
    if not isinstance(recipe, dict):
        raise ValueError("Il campo 'recipe' deve essere un oggetto.")

    details = recipe.get("details")
    if not isinstance(details, dict):
        raise ValueError("Il campo 'recipe.details' deve essere un oggetto.")

    ingredients = details.get("ingredients")
    if not isinstance(ingredients, list) or not ingredients:
        raise ValueError("Il campo 'recipe.details.ingredients' deve essere una lista non vuota.")

    if not all(isinstance(item, str) and item.strip() for item in ingredients):
        raise ValueError("Tutti gli elementi di 'recipe.details.ingredients' devono essere stringhe non vuote.")

    guessed_input = input_data.get("input")
    if not isinstance(guessed_input, str) or not guessed_input.strip():
        raise ValueError("Il campo 'input' deve essere una stringa non vuota.")


def build_output_document(
    input_data: dict[str, Any],
    result: dict[str, Any] | None,
) -> dict:
    return {
        "recipe": input_data.get("recipe"),
        "input": input_data.get("input"),
        "output": result,
    }


def validate_model_output(result: dict[str, Any], input_data: dict[str, Any]) -> None:
    """Valida la struttura dell'oggetto `output` restituito dal modello."""
    rating = result.get("rating")
    if not isinstance(rating, int) or not 0 <= rating <= 10:
        raise ValueError("Il campo 'output.rating' deve essere un intero tra 0 e 10.")

    response = result.get("response")
    if not isinstance(response, str) or not response.strip():
        raise ValueError("Il campo 'output.response' deve essere una stringa non vuota.")

    ingredients_map = result.get("ingredientsMap")
    if not isinstance(ingredients_map, list):
        raise ValueError("Il campo 'output.ingredientsMap' deve essere una lista.")

    correct_ingredients = input_data["recipe"]["details"]["ingredients"]
    if len(ingredients_map) != len(correct_ingredients):
        raise ValueError(
            "Il campo 'output.ingredientsMap' deve contenere una voce per ogni ingrediente corretto."
        )

    for item in ingredients_map:
        if not isinstance(item, dict):
            raise ValueError("Ogni elemento di 'output.ingredientsMap' deve essere un oggetto.")
        if not isinstance(item.get("correctIngredient"), str) or not item["correctIngredient"].strip():
            raise ValueError("Ogni elemento di 'output.ingredientsMap.correctIngredient' deve essere una stringa non vuota.")
        proposed = item.get("proposedIngredient")
        if proposed is not None and not isinstance(proposed, str):
            raise ValueError(
                "Ogni elemento di 'output.ingredientsMap.proposedIngredient' deve essere una stringa o null."
            )
        if not isinstance(item.get("accepted"), bool):
            raise ValueError("Ogni elemento di 'output.ingredientsMap.accepted' deve essere booleano.")


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

    try:
        validate_input_data(input_data)
    except ValueError as exc:
        print(f"[ERRORE] {exc}", file=sys.stderr)
        sys.exit(1)

    # --- Chiamata Together AI ---
    lib = TogetherLib(
        system_prompt=SYSTEM_PROMPT,
        output_schema=OUTPUT_SCHEMA,
        model=MODEL,
    )

    result: dict[str, Any] | None = None

    try:
        result = lib.run(input_data)
        validate_model_output(result, input_data)
        print(f"[OK] Risposta ricevuta dal modello.")
    except (ValueError, RuntimeError) as exc:
        print(f"[ERRORE] {exc}", file=sys.stderr)
        output = build_output_document(input_data, None)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"[OK] Output scritto in: {output_path}")
        sys.exit(1)

    # --- Scrittura output ---
    output = build_output_document(input_data, result)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"[OK] Output scritto in: {output_path}")


if __name__ == "__main__":
    main()
