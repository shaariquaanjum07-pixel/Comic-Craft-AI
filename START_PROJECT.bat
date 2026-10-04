@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo        ComicCraft - Starting App
echo ========================================

echo.
if not exist ".venv\Scripts\python.exe" (
    echo Creating Python virtual environment...
    py -m venv .venv
    if errorlevel 1 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

call ".venv\Scripts\activate.bat"

python -m pip install --upgrade pip
if errorlevel 1 (
    echo Failed to upgrade pip.
    pause
    exit /b 1
)

pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo ComicCraft is starting at http://127.0.0.1:8000
start "" http://127.0.0.1:8000
python -m uvicorn app.main:app --reload

pause
