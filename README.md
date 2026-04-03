# PoE Craft Regex

A Path of Exile crafting bench regex builder — visually select mods from the
crafting bench and instantly generate a regex string to paste into your crafting
bench.

## Stack

| Layer    | Technology          |
|----------|---------------------|
| Frontend | React + Tailwind CSS|
| Backend  | Python + FastAPI    |
| Data     | JSON (mod dataset)  |
| Hosting  | Vercel + Render     |


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

## Running the Frontend Locally

```bash
cd frontend
npm install
npm run dev
```

You should see the App at: http://localhost:5173
Make sure your backend is also running in a separate terminal

## API Endpoints

| Method | Endpoint           | Description                          |
|--------|--------------------|--------------------------------------|
| GET    | /health            | Liveness check                       |
| GET    | /mods              | All mods (supports ?slot= ?category=)|
| GET    | /mods/slots        | List of valid item slots             |
| GET    | /mods/categories   | List of mod categories               |
| GET    | /mods/{id}         | Single mod by ID                     |
| POST   | /mods/regex        | Generate regex from mod ID list      |
