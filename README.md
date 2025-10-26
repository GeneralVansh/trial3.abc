Praktiki — Full Demo Project
============================
This zip contains a demo frontend + backend for the Praktiki Internship Equivalence PoC.

Quick start (local):
1. Navigate to backend/
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8000

2. Open frontend/index.html in your browser (file://) or serve via simple server:
   python -m http.server 8001 (then open http://localhost:8001/frontend/index.html)

Demo credentials:
  Student -> username: student  password: 12345
  Mentor  -> username: mentor   password: admin

Notes:
  - This is a demo. Data is stored in-memory in backend and will be lost on restart.
  - For production, use a persistent DB, HTTPS, and proper auth.
