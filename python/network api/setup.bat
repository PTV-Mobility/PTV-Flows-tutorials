@echo off
echo PTV Flows Network API Tutorial - Quick Setup
echo ============================================
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Error: Failed to create virtual environment
    echo Make sure Python is installed and accessible
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ✅ Setup completed successfully!
echo.
echo To use the PTV Flows Network Downloader:
echo   1. Activate the environment: venv\Scripts\activate.bat
echo   2. Run the script: python ptv_flows_downloader.py
echo   3. Or run the example: python example.py
echo.
pause