# Together API experiment

Questa cartella contiene un piccolo esempio Python per chiamare Together AI:

- `main.py` legge un file JSON di input con `recipe`, `input` e `output`
- usa `TogetherLib` per confrontare gli ingredienti corretti con quelli proposti dall'utente
- scrive un file JSON finale con la stessa struttura dell'input, valorizzando `output`

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
  "recipe": {
    "id": "D92CEB87-C915-B4B1-9618-DD0C1EA4FA83",
    "image_url": "http://service.suedtirol.info/imageresizer/ImageHandler.ashx?src=images/articles/rezeptartikel/a92c47a0-ace9-489f-aba2-17f137d62540.jpg",
    "language": "it",
    "details": {
      "title": "Crema di mozzarella e pomodoro",
      "description": "Crema di mozzarella e pomodoro",
      "ingredients": [
        "250 g di Ricotta Alto Adige",
        "125 g di Mozzarella Alto Adige",
        "120 g di pomodori ciliegini"
      ],
      "preparation": "..."
    }
  },
  "input": "mozzarella, pomodori freschi, sale, olio, basilico",
  "output": null
}
```

Il campo `input` contiene la risposta libera dell'utente.
Il modello usa `recipe.details.ingredients` come ground truth e deve riempire `output`.

## Formato dell'output

Lo script salva un file `output.json` con questa struttura:

```json
{
  "recipe": {
    "id": "D92CEB87-C915-B4B1-9618-DD0C1EA4FA83",
    "image_url": "http://...",
    "language": "it",
    "details": {
      "title": "Crema di mozzarella e pomodoro",
      "description": "Crema di mozzarella e pomodoro",
      "ingredients": [
        "250 g di Ricotta Alto Adige",
        "125 g di Mozzarella Alto Adige"
      ],
      "preparation": "..."
    }
  },
  "input": "mozzarella, pomodori freschi, sale, olio, basilico",
  "output": {
    "rating": 6,
    "response": "Hai indovinato gli ingredienti principali...",
    "ingredientsMap": [
      {
        "correctIngredient": "125 g di Mozzarella Alto Adige",
        "proposedIngredient": "mozzarella",
        "accepted": true
      },
      {
        "correctIngredient": "250 g di Ricotta Alto Adige",
        "proposedIngredient": null,
        "accepted": false
      }
    ]
  }
}
```

## Personalizzazione

Se vuoi adattare il comportamento del modello, modifica in `main.py`:

- `SYSTEM_PROMPT`
- `OUTPUT_SCHEMA`
- `MODEL`
