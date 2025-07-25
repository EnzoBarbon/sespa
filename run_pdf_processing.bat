echo off
echo ===========================================
echo     PDF Processing - SESPA Document
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

REM Check if PDF file exists
if not exist "data\data.pdf" (
    echo ERROR: PDF file not found
    echo Please place your PDF file as: data\data.pdf
    echo.
    echo Current data folder contents:
    if exist "data" (
        dir /b "data"
    ) else (
        echo data folder does not exist
    )
    echo.
    pause
    exit /b 1


echo Processing PDF file...
echo.

REM Create output directory if it doesn't exist
if not exist "output" mkdir output

REM Ask user about filtering
echo Do you want to filter records from before 2008? (y/n)
set /p filter_choice="> "

if /i "%filter_choice%"=="y" (
    echo Running with 2008 filter...
    python extract.py --filter-2008
) else (
    echo Running without filter...
    python extract.py
)

echo.
echo ===========================================
echo          Processing Complete!
echo ===========================================
echo.
echo Results saved to:
echo   - output/py_output.json
echo   - output/py_output_with_calculation.json
echo   - situaciones.csv
echo   - vacation_report.xlsx (Excel report)
echo.
echo Check the files above for your results.
echo.
pause