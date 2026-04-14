import json
import os
import re
import urllib.request
import ssl

def clean_html_text(text):
    if not text:
        return ""
    # Remove HTML tags
    cleaned = re.sub(r'<[^>]+>', ' ', text)
    # Normalize whitespace
    return " ".join(cleaned.split()).strip()

def parse_ingredients(html_content):
    if not html_content:
        return []
    # Find all li tags
    lis = re.findall(r'<li[^>]*>(.*?)</li>', html_content, re.IGNORECASE | re.DOTALL)
    res = []
    for li in lis:
        cleaned = clean_html_text(li)
        if cleaned:
            res.append(cleaned)
    return res

def fetch_recipes():
    base_url = "https://api.tourism.testingmachine.eu/v1/Article?articletype=rezeptartikel"
    next_page = base_url
    
    recipes_dict = {}
    
    while next_page:
        print(f"Fetching: {next_page}")
        # Create unverified context if needed
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(next_page, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode())
        
        items = data.get("Items", [])
        for item in items:
            recipe_id = item.get("Id")
            if not recipe_id or recipe_id in recipes_dict:
                continue
                
            # Image URL
            image_url = None
            gallery = item.get("ImageGallery", [])
            if gallery and isinstance(gallery, list) and len(gallery) > 0:
                image_url = gallery[0].get("ImageUrl")
                
            languages_data = {}
            for lang in ["it", "en", "de"]:
                # Default empty
                lang_dict = {
                    "title": "",
                    "description": "",
                    "ingredients": [],
                    "preparation": ""
                }
                
                # Detail
                detail = item.get("Detail", {}).get(lang, {})
                if detail:
                    title = detail.get("Title")
                    if title:
                        lang_dict["title"] = str(title).strip()
                    
                    desc = detail.get("MetaDesc")
                    if desc:
                        lang_dict["description"] = str(desc).strip()
                
                # AdditionalArticleInfos
                add_infos = item.get("AdditionalArticleInfos", {}).get(lang, {})
                if add_infos:
                    elements = add_infos.get("Elements", {})
                    if elements:
                        ingredients_html = elements.get("zutat1", "")
                        lang_dict["ingredients"] = parse_ingredients(ingredients_html)
                        
                        prep_html = elements.get("zubereitungstext", "")
                        lang_dict["preparation"] = clean_html_text(prep_html)
                
                languages_data[lang] = lang_dict
                
            recipes_dict[recipe_id] = {
                "id": recipe_id,
                "image_url": image_url,
                "languages": languages_data
            }
            
        next_page_token = data.get("NextPage")
        if next_page_token:
            # Handle relative next page URL if applicable, though usually they are absolute
            if next_page_token.startswith("http"):
                next_page = next_page_token
            else:
                next_page = "https://api.tourism.testingmachine.eu" + next_page_token
        else:
            next_page = None

    return list(recipes_dict.values())

if __name__ == "__main__":
    recipes = fetch_recipes()
    
    # Target path: data/recipes.json relative to the root of the project
    # Assuming script is in backend/experiments/open_data_hub_apis/
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, "../../../"))
    data_dir = os.path.join(root_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    out_file = os.path.join(data_dir, "recipes.json")
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(recipes, f, indent=2, ensure_ascii=False)
        
    print(f"Saved {len(recipes)} recipes to {out_file}")
