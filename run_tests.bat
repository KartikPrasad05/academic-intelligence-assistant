@echo off
setlocal
cd /d "D:\AgriNet\AWS\P3"

echo =====================================================================
echo    CAMPUSINTEL: AUTOMATED TEST SUITE & ACADEMIC BENCHMARK RUNNER
echo =====================================================================
echo.

set "PY=.\venv\Scripts\python.exe"
if not exist "%PY%" (
    set "PY=C:\Users\Ganesh\anaconda3\python.exe"
)

echo [1/2] RUNNING AUTOMATED UNIT & INTEGRATION TESTS (Pytest)...
echo ---------------------------------------------------------------------
"%PY%" -m pytest tests/test_rag_pipeline.py -v
if errorlevel 1 (
    echo [!] Some tests failed or pytest is not installed.
    echo Attempting direct execution via evaluate.py...
)

echo.
echo [2/2] RUNNING OFFICIAL 50-QUESTION ACADEMIC BENCHMARK (evaluate.py)...
echo ---------------------------------------------------------------------
"%PY%" evaluate.py

echo.
echo =====================================================================
echo  TESTING COMPLETE! Review the output above or check:
echo  - D:\AgriNet\AWS\P3\evaluation_report.md
echo  - D:\AgriNet\AWS\P3\evaluation_results.json
echo =====================================================================
pause
