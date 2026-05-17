# RoomMatch

Sustav za pametno spajanje cimera — Flask backend + React frontend, povezan na Supabase (PostgreSQL).

## Struktura

```
RoomMatch/
├── backend/        # Flask API (Python)
└── frontend/       # React (Vite)
```

## Pokretanje — backend

```bash
cd backend
python -m venv .venv
#source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate            # Windows
pip install -r requirements.txt
flask --app app run --debug --port 5000
```

API je na `http://localhost:5000`.

## Pokretanje — frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend je na `http://localhost:5173`.

### Testovi

```bash
cd backend
.venv\Scripts\activate
pytest
pytest tests/unit -v
pytest tests/integration -v
```
