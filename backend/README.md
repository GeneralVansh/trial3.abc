Praktiki PoC - Backend + Frontend
---------------------------------
This package contains a simple frontend (single HTML file) and a FastAPI backend scaffold
to simulate the WMD + ABC flow in a PoC environment.

Structure:
- frontend/praktiki_with_login.html  (open in browser)
- backend/app/main.py                (FastAPI app)
- backend/requirements.txt
- backend/README.md

How to run backend (local):
1. cd backend
2. python3 -m venv .venv
3. source .venv/bin/activate
4. pip install -r requirements.txt
5. uvicorn app.main:app --reload --port 8000

The backend exposes:
- POST /submit_internship  (submit internship)
- POST /mentor/run_and_push/{internship_id}?keywords=...&mode=success|pending|failure
- POST /api/v2/credits/upload  (simulator)
- GET /api/v2/credits/status/{abc_token}

To connect frontend to backend: edit the frontend JS to call these endpoints with fetch().
