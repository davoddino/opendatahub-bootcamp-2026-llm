from typing import Dict, Any

def call_llm(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Funzione stub che verrà implementata dal collega.
    Riceve il dizionario intero inviato dal client e restituisce
    lo stesso dizionario con in più compilato il campo 'output'.
    """
    
    # Esempio fittizio di ritorno per simulare che il campo 'output' 
    # venga valorizzato o modificato
    data["output"] = {
        "rating": 5,
        "response": "Il collega deve completare questa funzione!",
        "ingredientsMap": []
    }
    
    return data
