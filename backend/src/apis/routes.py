import os
import sys

from fastapi import APIRouter, Body
from typing import Dict, Any

from ..utils.recipe_utils import get_random_recipe
from ..llm.util import call_llm

router = APIRouter()

@router.get("/sendnewrequest")
def send_new_request(language: str = "it"):
    """
    Ritorna una ricetta a caso, strutturata come in docs/structure.json,
    precompilando il campo 'recipe' e lasciando 'input' e 'output' vuoti/null.
    """
    # Restituisce una ricetta inizializzata col payload JSON desiderato
    return get_random_recipe(language)


@router.post("/sendingredients")
def send_ingredients(data: Dict[str, Any] = Body(...)):
    """
    Riceve in input la struttura JSON con il campo 'input' completato dall'utente
    e restituisce lo stesso JSON con il campo 'output' popolato dal LLM.
    """
    # Richiama la funzione di utility stubbata che il collega implementerà
    response_data = call_llm(data)
    
    return response_data
