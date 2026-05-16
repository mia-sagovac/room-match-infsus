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
source .venv/bin/activate          # Linux/Mac
# .venv\Scripts\activate           # Windows
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

## Supabase konekcija

U `.env` postaviti `DATABASE_URL`. U Supabase Project → Settings → Database, koristi:

- **Direktna konekcija** (port 5432) za development
- **Session pooler** (port 5432, host `aws-0-...pooler.supabase.com`) ako tvoja mreža blokira IPv6
- **Transaction pooler** (port 6543) NE koristiti sa SQLAlchemy — ne podržava prepared statements iz default queryja

Format:
```
DATABASE_URL=postgresql+psycopg2://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

Shema baze (`CreateBaze.txt`) i seed podaci (`PopuliranjeBaze.txt`) trebaju već biti pokrenuti u Supabase SQL editoru.

## IDE preporuka

**PyCharm Professional** — radi sa svim datotekama (Python + JS/React + SQL + .env), ima Database alat za Supabase, Flask run konfiguracije i dobar React/JSX support out of the box.

WebStorm odlično podržava React/Node ali Python tretira kao stranjski jezik (osnovni highlighting, bez debuggera, bez venv menadžmenta) — za ovaj projekt nije idealan.

Alternativa: **PyCharm Community** (besplatan) za backend + **VS Code** za frontend, ako nemaš Pro licencu.
```

## API rute (skraćeno)

| Metoda | Ruta                          | Opis                                |
| ------ | ----------------------------- | ----------------------------------- |
| POST   | `/api/auth/register`          | Registracija                        |
| POST   | `/api/auth/login`             | Prijava (vraća JWT)                 |
| GET    | `/api/me`                     | Trenutni korisnik                   |
| GET/PUT| `/api/profil`                 | Vlastiti profil                     |
| GET/PUT| `/api/preferencija`           | Vlastite preferencije               |
| GET    | `/api/pitanja`                | Aktivna pitanja upitnika            |
| POST   | `/api/upitnik`                | Spremi odgovore upitnika            |
| GET    | `/api/match/preporuke`        | Preporučeni cimeri (s filterima)    |
| POST   | `/api/match`                  | Stvori match (predloži)             |
| PATCH  | `/api/match/<id>`             | Prihvati/odbij match                |
| GET    | `/api/razgovori`              | Moji razgovori                      |
| GET    | `/api/razgovori/<id>/poruke`  | Poruke razgovora                    |
| POST   | `/api/razgovori/<id>/poruke`  | Pošalji poruku                      |
| GET/POST | `/api/oglasi`               | Lista / kreiranje oglasa            |
