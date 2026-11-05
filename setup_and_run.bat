@echo off
setlocal enabledelayedexpansion

echo =====================================================================
echo    CAMPUSINTEL: CLOUD RAG COLLEGE ASSISTANT - ONE-CLICK LAUNCHER
echo =====================================================================
echo.

cd /d "D:\AgriNet\AWS\P3"

:: 1. Check if 'py' launcher is available
where py >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_CMD=py"
    goto :PYTHON_FOUND
)

:: 2. Check if 'python' is in PATH
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_CMD=python"
    goto :PYTHON_FOUND
)

:: 3. Scan common Windows installation directories
set "CANDIDATES="
set "CANDIDATES=%CANDIDATES% "%LOCALAPPDATA%\Programs\Python\Python313\python.exe""
set "CANDIDATES=%CANDIDATES% "%LOCALAPPDATA%\Programs\Python\Python312\python.exe""
set "CANDIDATES=%CANDIDATES% "%LOCALAPPDATA%\Programs\Python\Python311\python.exe""
set "CANDIDATES=%CANDIDATES% "%LOCALAPPDATA%\Programs\Python\Python310\python.exe""
set "CANDIDATES=%CANDIDATES% "%LOCALAPPDATA%\Programs\Python\Python39\python.exe""
set "CANDIDATES=%CANDIDATES% "C:\Program Files\Python313\python.exe""
set "CANDIDATES=%CANDIDATES% "C:\Program Files\Python312\python.exe""
set "CANDIDATES=%CANDIDATES% "C:\Program Files\Python311\python.exe""
set "CANDIDATES=%CANDIDATES% "C:\Program Files\Python310\python.exe""
set "CANDIDATES=%CANDIDATES% "C:\Python312\python.exe""
set "CANDIDATES=%CANDIDATES% "C:\Python311\python.exe""
set "CANDIDATES=%CANDIDATES% "C:\Python310\python.exe""
set "CANDIDATES=%CANDIDATES% "%USERPROFILE%\anaconda3\python.exe""
set "CANDIDATES=%CANDIDATES% "%USERPROFILE%\miniconda3\python.exe""
set "CANDIDATES=%CANDIDATES% "C:\ProgramData\anaconda3\python.exe""
set "CANDIDATES=%CANDIDATES% "C:\ProgramData\miniconda3\python.exe""

for %%p in (%CANDIDATES%) do (
    if exist %%p (
        set "PYTHON_CMD=%%~p"
        goto :PYTHON_FOUND
    )
)

:: 4. If Python is not found, attempt auto-install via winget
echo [!] Python is not installed or not in your system PATH.
echo.
echo Attempting to install Python 3.11 automatically via Windows Package Manager (winget)...
where winget >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo Running: winget install Python.Python.3.11
    winget install -e --id Python.Python.3.11 --scope currentUser
    if %ERRORLEVEL% equ 0 (
        echo [OK] Python installed! Please close and reopen this terminal window.
        pause
        exit /b 0
    )
)

echo.
echo =====================================================================
echo  ACTION REQUIRED: PLEASE INSTALL PYTHON
echo =====================================================================
echo  1. Open your browser and go to: https://www.python.org/downloads/
echo  2. Download Python 3.11 or 3.12 installer.
echo  3. IMPORTANT: On the very first screen of the installer, check:
echo     [X] "Add python.exe to PATH"
echo  4. Click "Install Now".
echo  5. After installation completes, re-run this setup_and_run.bat script.
echo =====================================================================
pause
exit /b 1

:PYTHON_FOUND
echo [OK] Found Python: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

:: 5. Create Virtual Environment if not present
if not exist "venv\Scripts\activate.bat" (
    echo [1/3] Creating Python Virtual Environment (venv)...
    %PYTHON_CMD% -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo [!] Failed to create venv. Retrying without pip isolation...
        %PYTHON_CMD% -m venv --without-pip venv
    )
    echo [OK] Virtual environment created.
) else (
    echo [OK] Virtual environment already exists.
)

:: 6. Activate Virtual Environment
echo [2/3] Activating Virtual Environment...
call venv\Scripts\activate.bat

:: 7. Install / Verify Requirements
echo [3/3] Checking and Installing Dependencies...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt

echo.
echo =====================================================================
echo  STARTING CAMPUSINTEL CLOUD RAG ASSISTANT WEB APPLICATION...
echo =====================================================================
echo.
streamlit run app.py

pause
