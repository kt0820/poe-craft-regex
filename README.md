# PoE Craft Regex

A Path of Exile crafting bench regex builder — visually select mods from the
crafting bench and instantly generate a regex string to paste into your stash
search.

## Stack

| Layer    | Technology          |
|----------|---------------------|
| Frontend | React + Tailwind CSS |
| Backend  | Python + FastAPI    |
| Data     | JSON (mod dataset)  |
| Hosting  | Vercel + Render     |

## Project Structure

```
poe-craft-regex/
├── backend/          # FastAPI Python API
│   ├── main.py
│   ├── requirements.txt
│   ├── data/
│   │   └── crafting_bench_mods.json
│   └── app/
│       ├── models/
│       ├── routers/
│       └── services/
└── frontend/         # React app (coming soon)
```

## Running the Backend Locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

API docs available at: http://localhost:8000/docs

## Running Tests

```bash
cd backend
pytest tests/ -v
```

## API Endpoints

| Method | Endpoint           | Description                          |
|--------|--------------------|--------------------------------------|
| GET    | /health            | Liveness check                       |
| GET    | /mods              | All mods (supports ?slot= ?category=)|
| GET    | /mods/slots        | List of valid item slots             |
| GET    | /mods/categories   | List of mod categories               |
| GET    | /mods/{id}         | Single mod by ID                     |
| POST   | /mods/regex        | Generate regex from mod ID list      |
