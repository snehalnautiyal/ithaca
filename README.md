# Ithaca

**Your data, finally home.** A self-hosted, local-first AI workspace.

## Quick start

```bash
cd ~/Projects/ithaca
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and set a real SECRET_KEY

mkdir -p data
python app.py
# First boot prints the admin password — save it.
# Open http://127.0.0.1:7860
```

## Stack
- Backend: Python 3.11, FastAPI, Uvicorn, SQLAlchemy + SQLite
- Frontend: Vanilla JS / HTML / CSS
- Local models: Ollama (`ollama pull llama3.2`)
