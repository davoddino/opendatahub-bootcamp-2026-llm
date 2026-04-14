import os
import json
import random

def get_random_recipe(language: str) -> dict:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, "../../.."))
    candidate_paths = [
        os.path.join(script_dir, "../../../data/recipes.json"),
        os.path.join(script_dir, "../../experiments/open_data_hub_apis/recipes.json"),
    ]

    file_path = next((path for path in candidate_paths if os.path.exists(path)), None)

    if not file_path:
        structure_example_path = os.path.join(repo_root, "docs/structure_example.json")
        if os.path.exists(structure_example_path):
            with open(structure_example_path, "r", encoding="utf-8") as f:
                structure_example = json.load(f)
            recipe = structure_example.get("recipe", {})
            details = recipe.get("details", {})
            return {
                "recipe": {
                    "id": recipe.get("id"),
                    "image_url": recipe.get("image_url"),
                    "language": recipe.get("language", language),
                    "details": {
                        "title": details.get("title", ""),
                        "description": details.get("description", ""),
                        "ingredients": details.get("ingredients", []),
                        "preparation": details.get("preparation", ""),
                    },
                },
                "input": None,
                "output": None,
            }

        raise FileNotFoundError("Nessun file recipes.json trovato nei path previsti.")
    
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
