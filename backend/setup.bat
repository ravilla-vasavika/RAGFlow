@echo off

REM RAG Flow Backend Setup Script for Windows

echo ================================
echo RAG Flow Backend Setup
echo ================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✓ Python found: %PYTHON_VERSION%

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ================================
echo Setup Complete!
echo ================================
echo.
echo Next steps:
echo 1. Configure .env file with your OpenAI API key
echo 2. Run the application: python -m uvicorn app.main:app --reload
echo 3. Visit: http://localhost:8000/docs
echo.

pause
