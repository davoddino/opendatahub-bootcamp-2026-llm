"""
llm_logic.py
------------
Logica applicativa per valutare gli ingredienti proposti dall'utente con Together AI.
"""

import json
from pathlib import Path
from typing import Any

from .together_lib import DEFAULT_MODEL, TogetherLib


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
- `response` deve essere breve, utile e nella lingua della ricetta dicendo anche quali ingredienti sono stati omessi.
  Se il rating è basso, spiega cosa è stato indovinato e cosa no.
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
) -> dict[str, Any]:
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


def evaluate_recipe_guess(
    input_data: dict[str, Any],
    model: str = MODEL,
) -> dict[str, Any]:
    """
    Valuta gli ingredienti proposti dall'utente e restituisce il documento finale
    con `recipe`, `input` e `output`.
    """
    validate_input_data(input_data)

    lib = TogetherLib(
        system_prompt=SYSTEM_PROMPT,
        output_schema=OUTPUT_SCHEMA,
        model=model,
    )

    result = lib.run(input_data)
    validate_model_output(result, input_data)
    return build_output_document(input_data, result)


def process_input_file(
    input_path: str | Path,
    output_path: str | Path,
    model: str = MODEL,
) -> dict[str, Any]:
    """
    Legge un file JSON di input, invoca la logica LLM e scrive il documento finale.
    In caso di errore del modello, scrive comunque `output: null` e rilancia l'eccezione.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"File di input non trovato: {input_path}")

    with input_path.open(encoding="utf-8") as f:
        input_data: dict[str, Any] = json.load(f)

    try:
        output_document = evaluate_recipe_guess(input_data, model=model)
    except (RuntimeError, ValueError):
        fallback_document = build_output_document(input_data, None)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(fallback_document, f, ensure_ascii=False, indent=2)
        raise

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(output_document, f, ensure_ascii=False, indent=2)

    return output_document
