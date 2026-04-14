import os
from pathlib import Path

from dotenv import load_dotenv
from together import Together


def main() -> None:
    script_dir = Path(__file__).resolve().parent

    # Carica i file .env possibili, dal più specifico al più generale.
    load_dotenv(script_dir / ".env")
    load_dotenv(script_dir.parent / ".env")
    load_dotenv(script_dir.parent.parent / ".env")
    load_dotenv(script_dir.parent.parent.parent / ".env")

    api_key = os.environ.get("TOGETHER_API_KEY")
    if not api_key:
        raise RuntimeError(
            "TOGETHER_API_KEY non trovata. Aggiungila in backend/experiments/together_api/.env o in un .env del progetto."
        )

    client = Together(api_key=api_key)
    response = client.chat.completions.create(
        # model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        model="zai-org/GLM-5.1",
        messages=[{"role": "user", "content": "What is the capital of Italy?"}],
        response_format={
            "type": "json_object"
        }
    )


    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
