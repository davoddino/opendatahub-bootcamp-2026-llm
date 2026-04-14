# backend/src/main.py

import os
import sys
from fastapi import FastAPI
import uvicorn

# Assicuriamoci che python riesca a caricare il modulo dal livello corretto. 
# Quando testato avviando con `python backend/src/main.py`, questo forza il root in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.src.apis.routes import router

app = FastAPI(
    title="Open Data Hub API Backend",
    description="Backend per il Bootcamp sulle ricette e l'uso di LLM",
    version="1.0.0"
)

# Registra il router contenente tutte le nostre route (/sendnewrequest, /sendingredients)
app.include_router(router)

if __name__ == "__main__":
    # Avvia uvicorn in ascolto su tutte le interfacce per essere accessibile esternamente
    uvicorn.run("backend.src.main:app", host="0.0.0.0", port=8000, reload=True)
