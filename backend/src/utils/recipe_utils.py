import os
import json
import random

def get_random_recipe(language: str) -> dict:
    # Calcola il percorso al file dei dati rispetto a questo script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "../../../data/recipes.json")
    
    with open(file_path, "r", encoding="utf-8") as f:
        recipes = json.load(f)
        
    # Filtra per assicurarsi che la ricetta abbia almeno il titolo nella lingua scelta
    valid_recipes = [r for r in recipes if r.get("languages", {}).get(language, {}).get("title")]
    
    # Fallback nel caso in cui non ci siano risultati
    if not valid_recipes:
        valid_recipes = recipes
        
    recipe = random.choice(valid_recipes)
    lang_details = recipe.get("languages", {}).get(language, {
        "title": "",
        "description": "",
        "ingredients": [],
        "preparation": ""
    })
    
    return {
        "recipe": {
            "id": recipe.get("id"),
            "image_url": recipe.get("image_url"),
            "language": language,
            "details": {
                "title": lang_details.get("title", ""),
                "description": lang_details.get("description", ""),
                "ingredients": lang_details.get("ingredients", []),
                "preparation": lang_details.get("preparation", "")
            }
        },
        "input": None,
        "output": None
    }
