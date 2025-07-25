@echo off
echo ===========================================
echo     OCR Processing - SESPA Document
echo ===========================================
echo.

REM Check if setup was run
if not exist "venv" (
    echo ERROR: Virtual environment not found
    echo Please run setup_windows.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if images folder exists
if not exist "data\imagenes" (
    echo ERROR: Images folder not found
    echo Please create folder: data\imagenes
    echo And place your document images there
    echo.
    pause
    exit /b 1
)

REM Check if there are any images
dir /b "data\imagenes\*.jpg" "data\imagenes\*.jpeg" "data\imagenes\*.png" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: No image files found in data\imagenes
    echo Please place your document images (.jpg, .jpeg, .png) in:
    echo data\imagenes\
    echo.
    echo Current imagenes folder contents:
    dir /b "data\imagenes"
    echo.
    pause
    exit /b 1
)

echo Found images to process:
dir /b "data\imagenes\*.jpg" "data\imagenes\*.jpeg" "data\imagenes\*.png" 2>nul
echo.

REM Create output directory if it doesn't exist
if not exist "output" mkdir output

REM Ask user about filtering
echo Do you want to filter records from before 2008? (y/n)
set /p filter_choice="> "

echo.
echo Starting OCR processing...
echo This may take several minutes depending on image quality and quantity.
echo.

if /i "%filter_choice%"=="y" (
    echo Running with 2008 filter...
    python extract.py --use-ocr --filter-2008
) else (
    echo Running without filter...
    python extract.py --use-ocr
)

echo.
echo ===========================================
echo          Processing Complete!
echo ===========================================
echo.
echo Results saved to:
echo   - output/py_output.json
echo   - output/py_output_with_calculation.json
echo   - output/py_output_with_calculation_ocr.json
echo   - vacation_report.xlsx (Excel report)
echo.
echo Check the files above for your results.
echo.
pause