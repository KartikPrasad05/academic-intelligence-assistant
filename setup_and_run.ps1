# =====================================================================
# CAMPUSINTEL: CLOUD RAG COLLEGE ASSISTANT - POWERSHELL SETUP & RUNNER
# =====================================================================

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "   CAMPUSINTEL: CLOUD RAG COLLEGE ASSISTANT - POWERSHELL RUNNER" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location -Path "D:\AgriNet\AWS\P3"

# 1. Look for Python via py launcher, python, or common installation paths
$pythonPath = $null

if (Get-Command "py" -ErrorAction SilentlyContinue) {
    $pythonPath = "py"
} elseif (Get-Command "python" -ErrorAction SilentlyContinue) {
    $pythonPath = "python"
} else {
    $candidatePaths = @(
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python39\python.exe",
        "C:\Program Files\Python313\python.exe",
        "C:\Program Files\Python312\python.exe",
        "C:\Program Files\Python311\python.exe",
        "C:\Program Files\Python310\python.exe",
        "C:\Python312\python.exe",
        "C:\Python311\python.exe",
        "C:\Python310\python.exe",
        "$env:USERPROFILE\anaconda3\python.exe",
        "$env:USERPROFILE\miniconda3\python.exe",
        "C:\ProgramData\anaconda3\python.exe",
        "C:\ProgramData\miniconda3\python.exe"
    )

    foreach ($path in $candidatePaths) {
        if (Test-Path $path) {
            $pythonPath = $path
            break
        }
    }
}

if (-not $pythonPath) {
    Write-Host "[!] Python was not detected in PATH or standard installation folders." -ForegroundColor Red
    Write-Host ""
    
    if (Get-Command "winget" -ErrorAction SilentlyContinue) {
        Write-Host "Attempting automatic installation of Python 3.11 via winget..." -ForegroundColor Yellow
        winget install -e --id Python.Python.3.11 --scope currentUser
        Write-Host ""
        Write-Host "[OK] Installation completed. Please close and re-open this PowerShell window so PATH is reloaded." -ForegroundColor Green
        return
    }

    Write-Host "Please install Python manually:" -ForegroundColor Yellow
    Write-Host "1. Download from https://www.python.org/downloads/" -ForegroundColor White
    Write-Host "2. CRITICAL: Check the box '[X] Add python.exe to PATH' during installation" -ForegroundColor White
    Write-Host "3. Re-run this script after installation." -ForegroundColor White
    return
}

Write-Host "[OK] Detected Python executable: $pythonPath" -ForegroundColor Green
& $pythonPath --version
Write-Host ""

# 2. Create Virtual Environment
if (-not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "[1/3] Creating Python Virtual Environment (venv)..." -ForegroundColor Yellow
    & $pythonPath -m venv venv
    Write-Host "[OK] Virtual Environment created." -ForegroundColor Green
} else {
    Write-Host "[OK] Virtual Environment already exists." -ForegroundColor Green
}

# 3. Activate Virtual Environment
Write-Host "[2/3] Activating Virtual Environment..." -ForegroundColor Yellow
$activateScript = ".\venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
}

# 4. Install Dependencies
Write-Host "[3/3] Verifying and installing dependencies..." -ForegroundColor Yellow
& python -m pip install --upgrade pip
& pip install -r requirements.txt

# 5. Launch Streamlit Application
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  LAUNCHING CAMPUSINTEL STREAMLIT WEB APPLICATION..." -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""
& streamlit run app.py
