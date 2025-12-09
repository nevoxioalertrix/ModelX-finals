@echo off
title Sri Lanka Business Intelligence Platform
color 0A

echo ================================================================================
echo        SRI LANKA BUSINESS INTELLIGENCE PLATFORM
echo        Real-Time Situational Awareness System
echo ================================================================================
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo [INFO] Virtual environment not found. Creating one...
    echo.
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        echo         Make sure Python is installed and in your PATH.
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created.
    echo.
    
    echo [INFO] Installing dependencies...
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
    echo [SUCCESS] Dependencies installed.
    echo.
) else (
    call .venv\Scripts\activate.bat
)

echo [INFO] Starting the dashboard...
echo [INFO] Opening browser at http://localhost:8501
echo.
echo ================================================================================
echo  Dashboard is running! Close this window to stop the server.
echo ================================================================================
echo.

REM Open browser after a short delay
start "" http://localhost:8501

REM Run Streamlit
python -m streamlit run app.py --server.headless true

pause
