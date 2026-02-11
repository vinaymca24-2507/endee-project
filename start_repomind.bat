@echo off
echo ==========================================
echo Starting RepoMind...
echo ==========================================

echo [1/3] Starting Endee Vector DB (Docker)...
docker compose up -d endee
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to start Endee. Is Docker Desktop running?
    pause
    exit /b %ERRORLEVEL%
)


echo [2/4] Starting Ollama (Local LLM)...
start "Ollama" cmd /k "ollama run mistral"
timeout /t 5

echo [3/4] Starting Backend API...
start "RepoMind API" cmd /k "uvicorn api.main:app --reload"

echo [4/4] Starting Frontend UI...
start "RepoMind UI" cmd /k "streamlit run ui/app.py"

echo ==========================================
echo RepoMind is starting!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:8501
echo ==========================================
pause
