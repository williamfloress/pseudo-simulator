$env:PYTHONPATH = "backend"
.\venv\Scripts\uvicorn main:app --host 127.0.0.1 --port 8000 --app-dir backend
