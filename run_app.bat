@echo off
setlocal
cd /d "D:\AgriNet\AWS\P3"

echo =====================================================================
echo    CAMPUSINTEL: CLOUD RAG COLLEGE ASSISTANT (ONE-CLICK LAUNCHER)
echo =====================================================================
echo.

set "PYTHON_EXE=C:\Users\Ganesh\anaconda3\python.exe"

if not exist "%PYTHON_EXE%" (
    echo [!] Python not found at %PYTHON_EXE%
    pause
    exit /b 1
)

echo [OK] Using Python: %PYTHON_EXE%
echo.

if not exist "venv\Scripts\python.exe" (
    echo [1/3] Creating virtual environment in D:\AgriNet\AWS\P3\venv...
    "%PYTHON_EXE%" -m venv venv
    if errorlevel 1 (
        echo [!] Failed to create venv. Using Anaconda Python directly...
        goto :INSTALL_DIRECT
    )
    echo [OK] Virtual environment created.
)

:INSTALL_VENV
echo [2/3] Installing dependencies into venv...
".\venv\Scripts\pip.exe" install -r requirements.txt
echo.
echo [3/3] Launching CampusIntel Cloud RAG Web Application...
".\venv\Scripts\streamlit.exe" run app.py
goto :END

:INSTALL_DIRECT
echo [2/3] Installing dependencies into Anaconda environment...
"%PYTHON_EXE%" -m pip install -r requirements.txt
echo.
echo [3/3] Launching CampusIntel Cloud RAG Web Application...
"%PYTHON_EXE%" -m streamlit run app.py

:END
pause
