@echo off
echo.
echo  ==========================================
echo        Welcome to HireWise - Arun
echo  ==========================================
echo.

:: Step 1 - Create virtual environment if not exists
IF NOT EXIST "venv\" (
    echo  [1/3] Setting up for first time... Please wait...
    python -m venv venv
    echo  Done!
) ELSE (
    echo  [1/3] Setup already done. Skipping...
)

:: Step 2 - Activate and install requirements
echo  [2/3] Installing required packages...
call venv\Scripts\activate
pip install -r requirements.txt --quiet

:: Step 3 - Open browser and start app
echo  [3/3] Starting HireWise...
echo.
echo  ==========================================
echo   App is running! Opening your browser...
echo   To STOP the app, close this window.
echo  ==========================================
echo.

start http://localhost:5000
python app.py

pause
