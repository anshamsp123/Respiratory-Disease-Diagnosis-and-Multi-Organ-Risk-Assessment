@echo off
echo Starting FastAPI Backend...
start cmd /k "uvicorn api.main:app --reload --port 8000"

echo Starting Streamlit Frontend...
start cmd /k "streamlit run ui/app.py"

echo System is running!
