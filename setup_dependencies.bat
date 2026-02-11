@echo off
echo ==========================================
echo Installing RepoMind Dependencies...
echo ==========================================

echo [1/2] Installing requirements.txt...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install requirements.txt. Make sure Python is installed.
    pause
    exit /b %ERRORLEVEL%
)

echo [2/2] Installing MessagePack (required for Endee metadata)...
pip install msgpack
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install msgpack.
    pause
    exit /b %ERRORLEVEL%
)

echo ==========================================
echo Dependencies installed successfully!
echo You can now run start_repomind.bat
echo ==========================================
pause
