from typing import Dict, Any

from .llm_logic import evaluate_recipe_guess


def call_llm(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Riceve il dizionario intero inviato dal client e restituisce
    lo stesso dizionario con il campo `output` compilato dal LLM.
    """
    return evaluate_recipe_guess(data)
