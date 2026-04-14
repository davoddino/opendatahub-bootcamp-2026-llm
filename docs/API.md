# Open Data Hub Bootcamp 2026 - API Guidelines

Il server FastAPI per simulare la generazione della ricetta e l'indovina-ingredienti dell'LLM. 

Entrambe si basano su uno schema dati JSON conforme a `docs/structure.json`.

---

## 1. GET `/sendnewrequest`
Questa API restituisce una nuova ricetta presa casualmente dal mock data `data/recipes.json`, strutturata secondo lo schema e formattandola in base alla lingua richiesta.

- **Query Parameter**: `language` (es. `it`, `en`, `de`) – Default: `it`
- **Output**: JSON della struttura iniziale con `input` e `output` impostati a `null`.

**Esempio di cURL:**
```bash
curl -X GET "http://localhost:8000/sendnewrequest?language=it"
```

## 2. POST `/sendingredients`
Questa API viene invocata dal client dopo che l'utente ha riempito il campo `"input"`. Prende in ingresso l'intero JSON e lo passa all'LLM (mockato in dev fino ad integrazione).

Ritornerà lo stesso JSON da te inviato dove però il nodo `"output"` viene compilato dal modello IA con un `rating`, `response` testuale per il giocatore e analizzando in `ingredientsMap` le correttezza sulle parti indovinate o sfuggite.

- **Body (Raw JSON)**: Rispettare lo schema di `structure.json` fornendo il campo `input` completo da parte dell'utente.

**Esempio di cURL:**

```bash
curl -X POST "http://localhost:8000/sendingredients" \
     -H "Content-Type: application/json" \
     -d '{
            "recipe": {
              "language": "it",
              "details": {
                "title": "Crema di mozzarella e pomodoro"
              }
            },
            "input": "credo ci sia la mozzarella",
            "output": null
          }'
```