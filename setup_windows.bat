@echo off
echo ===========================================
echo    SESPA Document Processor Setup
echo ===========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found. Installing dependencies...
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install requirements
echo Installing Python packages...
pip install -r requirements.txt

REM Check if Ghostscript is installed (required for PDF processing)
echo.
echo Checking for Ghostscript...
gs --version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Ghostscript not found
    echo PDF processing may not work properly
    echo Please download and install Ghostscript from:
    echo https://www.ghostscript.com/download/gsdnld.html
    echo.
)

echo.
echo ===========================================
echo           Setup Complete!
echo ===========================================
echo.
echo You can now run:
echo   - run_pdf_processing.bat (for PDF files)
echo   - run_ocr_processing.bat (for image files)
echo.
pause