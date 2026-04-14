from typing import Dict, Any, Optional


def _fallback_evaluate_recipe_guess(data: Dict[str, Any], reason: Optional[str] = None) -> Dict[str, Any]:
    recipe = data.get("recipe") or {}
    details = recipe.get("details") or {}
    correct_ingredients = details.get("ingredients") or []
    user_input = (data.get("input") or "").lower()

    ingredients_map = []
    accepted_count = 0

    for ingredient in correct_ingredients:
        normalized = ingredient.lower()
        candidate = ingredient if any(token in user_input for token in normalized.split()) else None
        accepted = candidate is not None
        if accepted:
            accepted_count += 1
        ingredients_map.append(
            {
                "correctIngredient": ingredient,
                "proposedIngredient": candidate,
                "accepted": accepted,
            }
        )

    rating = int(round((accepted_count / max(len(correct_ingredients), 1)) * 10))
    response = "Valutazione locale temporanea."
    if reason:
        response = f"{response} Motivo fallback: {reason}"
    else:
        response = f"{response} Configura TOGETHER_API_KEY per usare il modello LLM."

    return {
        "recipe": recipe,
        "input": data.get("input"),
        "output": {
            "rating": rating,
            "response": response,
            "ingredientsMap": ingredients_map,
        },
    }


def call_llm(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Riceve il dizionario intero inviato dal client e restituisce
    lo stesso dizionario con il campo `output` compilato dal LLM.
    """
    try:
        from .llm_logic import evaluate_recipe_guess

        return evaluate_recipe_guess(data)
    except (ImportError, RuntimeError):
        return _fallback_evaluate_recipe_guess(data, reason="Together API non disponibile o richiesta rifiutata")
