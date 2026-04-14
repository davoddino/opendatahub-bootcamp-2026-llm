"""
together_image.py
-----------------
Genera immagini piccole e divertenti per la presentazione a partire da PRESENTATION.md
usando Together AI image generation.

Esempio:
    uv run python backend/experiments/together_api/together_image.py
    uv run python backend/experiments/together_api/together_image.py --limit 4
"""

import argparse
import base64
import io
import json
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from PIL import Image
from together import Together


DEFAULT_MODEL = "google/flash-image-2.5"
DEFAULT_REQUEST_WIDTH = 1024
DEFAULT_REQUEST_HEIGHT = 1024
DEFAULT_SAVE_WIDTH = 512
DEFAULT_SAVE_HEIGHT = 512


def load_env() -> None:
    """Carica i file .env possibili, dal più specifico al più generale."""
    script_dir = Path(__file__).resolve().parent
    load_dotenv(script_dir / ".env")
    load_dotenv(script_dir.parent / ".env")
    load_dotenv(script_dir.parent.parent / ".env")
    load_dotenv(script_dir.parent.parent.parent / ".env")


def parse_presentation(markdown_path: Path) -> list[dict[str, Any]]:
    """Estrae le slide da PRESENTATION.md."""
    text = markdown_path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"^### Slide (?P<number>\d+)\. (?P<section>[^\n]+)\n(?P<body>.*?)(?=^### Slide \d+\. |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    slides: list[dict[str, Any]] = []

    for match in pattern.finditer(text):
        body = match.group("body")
        title = extract_markdown_field(body, "Title")
        key_message = extract_markdown_field(body, "Key message")
        notes = extract_markdown_field(body, "What to say")
        slides.append(
            {
                "number": int(match.group("number")),
                "section": match.group("section").strip(),
                "title": title or match.group("section").strip(),
                "key_message": key_message or "",
                "notes": notes or "",
            }
        )

    if not slides:
        raise ValueError(f"Nessuna slide trovata in {markdown_path}")
    return slides


def extract_markdown_field(body: str, label: str) -> str:
    """Estrae il paragrafo che segue un campo markdown tipo **Title:**."""
    pattern = re.compile(
        rf"\*\*{re.escape(label)}:\*\*\n(?P<value>.*?)(?=\n\*\*[^\n]+:\*\*|\n### |\Z)",
        re.DOTALL,
    )
    match = pattern.search(body)
    if not match:
        return ""
    return " ".join(line.strip() for line in match.group("value").strip().splitlines())


def build_prompt(slide: dict[str, Any]) -> str:
    """Costruisce un prompt visivo breve e coerente con la slide."""
    number = slide["number"]
    title = slide["title"]
    key_message = slide["key_message"]

    base_style = (
        "playful presentation illustration, compact square composition, colorful, fun, clean, "
        "friendly shapes, modern flat-cartoon style, light background, high contrast, "
        "simple objects, no readable text, suitable for a tech project slide"
    )

    prompts_by_slide = {
        1: (
            "A cheerful food trivia scene with a recipe photo card, magnifying glass, tomato, mozzarella, "
            "basil leaves, and floating question marks, showing the idea of guessing ingredients from a photo."
        ),
        2: (
            "A clean visual about open data: recipe card, data nodes, JSON brackets, a small database icon, "
            "and an alpine food vibe, representing recipes coming from Open Data Hub."
        ),
        3: (
            "A simple workflow pipeline: random recipe data, recipe image, user typing guessed ingredients, "
            "an AI assistant icon, and a JSON response card with arrows between each step."
        ),
        4: (
            "A friendly AI chef robot comparing an ingredient checklist, with green check marks and red crosses, "
            "showing how the LLM compares guessed ingredients with the correct recipe ingredients."
        ),
        5: (
            "A fun quiz game interface with five recipe rounds, small food images, a score bar, and a final result badge, "
            "showing a player receiving feedback after each guess."
        ),
        6: (
            "A future-features concept scene with a trophy scoreboard on one side and a restaurant discount coupon "
            "on the other, with playful food and reward icons."
        ),
    }

    custom_prompt = prompts_by_slide.get(
        number,
        (
            f"An illustration for a slide titled {title}. "
            f"It should visually express: {key_message}."
        ),
    )
    return f"{custom_prompt} {base_style}"


def generate_image(
    client: Together,
    prompt: str,
    model: str,
    width: int,
    height: int,
    seed: int,
) -> bytes:
    """Genera un'immagine Together e restituisce i bytes PNG."""
    response = client.images.generate(
        prompt=prompt,
        model=model,
        width=width,
        height=height,
        output_format="png",
        response_format="base64",
        seed=seed,
    )
    encoded = response.data[0].b64_json
    return base64.b64decode(encoded)


def resize_png(image_bytes: bytes, width: int, height: int) -> bytes:
    """Ridimensiona il PNG finale per ottenere immagini più compatte per le slide."""
    with Image.open(io.BytesIO(image_bytes)) as image:
        resized = image.resize((width, height), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        resized.save(buffer, format="PNG")
        return buffer.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera immagini Together AI per le slide della presentazione."
    )
    parser.add_argument(
        "--input",
        "-i",
        default="PRESENTATION.md",
        help="File markdown della presentazione (default: PRESENTATION.md nella root del repo).",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Modello Together images da usare (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=DEFAULT_REQUEST_WIDTH,
        help=f"Larghezza richiesta al modello (default: {DEFAULT_REQUEST_WIDTH})",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=DEFAULT_REQUEST_HEIGHT,
        help=f"Altezza richiesta al modello (default: {DEFAULT_REQUEST_HEIGHT})",
    )
    parser.add_argument(
        "--save-width",
        type=int,
        default=DEFAULT_SAVE_WIDTH,
        help=f"Larghezza finale dei PNG salvati (default: {DEFAULT_SAVE_WIDTH})",
    )
    parser.add_argument(
        "--save-height",
        type=int,
        default=DEFAULT_SAVE_HEIGHT,
        help=f"Altezza finale dei PNG salvati (default: {DEFAULT_SAVE_HEIGHT})",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=6,
        help="Numero massimo di slide da elaborare (default: 6)",
    )
    args = parser.parse_args()

    load_env()

    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent.parent
    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = repo_root / input_path

    slides = parse_presentation(input_path)[: args.limit]
    client = Together()

    manifest: list[dict[str, Any]] = []

    for slide in slides:
        prompt = build_prompt(slide)
        image_bytes = generate_image(
            client=client,
            prompt=prompt,
            model=args.model,
            width=args.width,
            height=args.height,
            seed=1000 + slide["number"],
        )
        image_bytes = resize_png(image_bytes, args.save_width, args.save_height)
        image_name = f"presentation_slide_{slide['number']:02d}.png"
        image_path = script_dir / image_name
        image_path.write_bytes(image_bytes)

        manifest.append(
            {
                "slide": slide["number"],
                "title": slide["title"],
                "image": image_name,
                "prompt": prompt,
            }
        )
        print(f"[OK] Generata immagine slide {slide['number']}: {image_path}")

    manifest_path = script_dir / "presentation_images_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[OK] Manifest scritto in: {manifest_path}")


if __name__ == "__main__":
    main()
