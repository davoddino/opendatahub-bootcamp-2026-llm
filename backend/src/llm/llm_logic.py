"""
llm_logic.py
------------
Logica applicativa per valutare gli ingredienti proposti dall'utente con Together AI.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .together_lib import DEFAULT_MODEL, TogetherLib


SYSTEM_PROMPT = """
You are an assistant that evaluates the ingredients guessed by a user for a recipe.
You must reply ALWAYS and ONLY with a valid JSON object, without any additional text.
Strictly adhere to the JSON schema provided in the user request.

You must exclusively use these input fields:
- `recipe.details.ingredients`: the official list of the correct recipe ingredients.
- `input`: the user's free-text response with the ingredients they think are used.

CRITICAL RULES FOR `ingredientsMap`:
- `ingredientsMap` MUST ALWAYS be an array strictly preserving the exact length and content of `recipe.details.ingredients`. If the original recipe has 10 ingredients, the map MUST have exactly 10 items.
- Iterating over each item from `recipe.details.ingredients`:
  * Map it to `correctIngredient` exactly as it's written in the original recipe.
  * Evaluate the user's `input` to find out if they guessed it (semantically).
  * If they guessed it, set `proposedIngredient` to what they guessed and `accepted` to `true`.
  * If they MISS the item entirely, or guess something unrelated, set `proposedIngredient` to `null` and `accepted` to `false`.

General Rules:
- Ignore `output` if present in the input.
- Compare semantically, not just textually (e.g. "mozzarella" matches "125 g of Mozzarella Alto Adige").
- `rating` must be an integer from 0 to 10 evaluating how much they guessed right over the total ingredients.
- `response` must be a short paragraph IN THE SAME LANGUAGE of the recipe (deduced by the input data language). Mention what was guessed correctly and what was missed.
""".strip()

OUTPUT_SCHEMA = {
    "rating": "integer from 0 to 10 based on how many ingredients guessed correctly",
    "response": "brief feedback for the user written strictly in the same language of the recipe explaining what is right and wrong",
    "ingredientsMap": [
        {
            "correctIngredient": "one EXACT string token from recipe.details.ingredients",
            "proposedIngredient": "what the user guessed for this correctIngredient or null",
            "accepted": "boolean: true if proposed is semantic match for correctIngredient, false if missed or proposed is null",
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
