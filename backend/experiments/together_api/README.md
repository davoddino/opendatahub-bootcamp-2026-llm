# Together API experiment

Questa cartella contiene un piccolo esempio Python per chiamare Together AI:

- `main.py` legge un file JSON di input
- usa `TogetherLib` per fare la richiesta al modello
- scrive la risposta in un file JSON di output

## File principali

- `main.py`: script da eseguire
- `together_lib.py`: wrapper riutilizzabile per Together AI
- `input.json`: esempio di input

## Prerequisiti

- Python `>=3.11`
- `uv` installato
- una chiave API Together valida

## Configurazione

### 1. Sincronizza l'ambiente con `uv`

Dalla root del repository:

```bash
uv sync
```

`python-dotenv` e le altre dipendenze necessarie sono già dichiarate nel progetto.

### 2. Configura la chiave API

Puoi usare una variabile d'ambiente oppure un file `.env`.

Opzione consigliata: copia l'esempio locale e inserisci la chiave:

```bash
cp backend/experiments/together_api/.env.example backend/experiments/together_api/.env
```

Contenuto richiesto:

```env
TOGETHER_API_KEY=la_tua_chiave_api
```

In alternativa puoi esportare la variabile prima dell'esecuzione:

```bash
export TOGETHER_API_KEY=la_tua_chiave_api
```

Nota: `together_lib.py` cerca il file `.env` in questi percorsi:

- `backend/experiments/together_api/.env`
- `backend/experiments/.env`
- `backend/.env`
- `.env` nella root del repository

## Come usare `main.py`

### Esecuzione dalla cartella dell'esperimento

Questo è il modo più semplice, perché `main.py` usa di default `input.json` e `output.json` relativi alla cartella corrente:

```bash
cd backend/experiments/together_api
uv run python main.py
```

Output atteso:

- legge `input.json`
- chiama Together AI
- scrive `output.json`

### Esecuzione dalla root del repository

Se vuoi lanciare lo script dalla root, devi passare i percorsi espliciti:

```bash
uv run python backend/experiments/together_api/main.py \
  --input backend/experiments/together_api/input.json \
  --output backend/experiments/together_api/output.json
```

## Argomenti disponibili

Puoi vedere l'help con:

```bash
uv run python backend/experiments/together_api/main.py --help
```

Argomenti supportati:

- `--input` oppure `-i`: file JSON di input
- `--output` oppure `-o`: file JSON di output

Esempio:

```bash
uv run python backend/experiments/together_api/main.py \
  --input backend/experiments/together_api/input.json \
  --output backend/experiments/together_api/output_custom.json
```

## Formato dell'input

Esempio di `input.json`:

```json
{
  "question": "Qual è la capitale d'Italia e quanti abitanti ha circa?",
  "language": "it"
}
```

## Formato dell'output

Lo script salva un file `output.json` con questa struttura:

```json
{
  "metadata": {
    "timestamp": "2026-04-14T10:00:00+00:00",
    "status": "success",
    "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo"
  },
  "input": {
    "question": "Qual è la capitale d'Italia e quanti abitanti ha circa?",
    "language": "it"
  },
  "result": {
    "answer": "...",
    "explanation": "...",
    "confidence": 0.95,
    "language": "it",
    "sources_hint": ""
  },
  "error": null
}
```

## Personalizzazione

Se vuoi adattare il comportamento del modello, modifica in `main.py`:

- `SYSTEM_PROMPT`
- `OUTPUT_SCHEMA`
- `MODEL`
