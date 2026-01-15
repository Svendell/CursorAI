@echo off
REM Steam Auth Manager - Quick Setup Script for Windows

echo ==========================================
echo Steam Auth Manager - Quick Setup (Windows)
echo ==========================================
echo.

REM Проверить Python
echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo OK - Python %PYTHON_VERSION% found
echo.

REM Создать виртуальное окружение
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo OK - Virtual environment created
) else (
    echo OK - Virtual environment already exists
)
echo.

REM Активировать виртуальное окружение
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo OK - Virtual environment activated
echo.

REM Установить зависимости
echo Installing dependencies...
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
echo OK - Dependencies installed
echo.

REM Создать необходимые папки
echo Creating directories...
if not exist "mafiles" mkdir mafiles
if not exist "backups" mkdir backups
if not exist "logs" mkdir logs
if not exist "data" mkdir data
echo OK - Directories created
echo.

REM Показать инструкции
echo ==========================================
echo OK - Setup completed successfully!
echo ==========================================
echo.
echo To run the application:
echo.
echo   venv\Scripts\activate
echo   python main.py
echo.
echo To run tests:
echo   python tests.py
echo.
echo To see examples:
echo   python example.py help
echo.
echo Documentation:
echo   - README.md
echo   - INSTALL.md
echo   - DEVELOPER_GUIDE.md
echo   - PROJECT_SUMMARY.md
echo.
echo ==========================================
echo.
pause
