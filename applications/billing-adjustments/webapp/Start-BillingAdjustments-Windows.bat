@echo off
REM Double-click this file to start the Billing Adjustments app.
REM First run sets everything up automatically; later runs start instantly.

cd /d "%~dp0"

echo ============================================================
echo   AWS Marketplace Billing Adjustments
echo ============================================================
echo.

REM 1. Find Python 3
set "PYTHON="
where py >nul 2>&1 && set "PYTHON=py -3"
if not defined PYTHON (
  where python >nul 2>&1 && set "PYTHON=python"
)

if not defined PYTHON (
  echo ERROR: Python 3.8+ was not found on this PC.
  echo.
  echo Please install Python from https://www.python.org/downloads/
  echo During install, CHECK the box "Add Python to PATH".
  echo Then double-click this file again.
  echo.
  pause
  exit /b 1
)

for /f "delims=" %%v in ('%PYTHON% --version 2^>^&1') do echo Using %%v

REM 2. Create a private virtual environment on first run
set "VENV_DIR=.venv_billing"
if not exist "%VENV_DIR%" (
  echo First-time setup: creating environment ^(this happens only once^)...
  %PYTHON% -m venv "%VENV_DIR%"
  if errorlevel 1 (
    echo Failed to create environment.
    pause
    exit /b 1
  )
)

REM 3. Activate it
call "%VENV_DIR%\Scripts\activate.bat"

REM 4. Install / update dependencies
echo Checking dependencies...
python -m pip install --quiet --upgrade pip >nul 2>&1
python -m pip install --quiet -r ..\requirements.txt
if errorlevel 1 (
  python -m pip install --quiet flask werkzeug "boto3>=1.42.80"
)

REM 5. Start the app (it opens your browser automatically)
echo.
echo Starting the app and opening your browser...
echo Keep this window open while you work. Close it to stop the app.
echo.
python app.py

echo.
echo The app has stopped.
pause
