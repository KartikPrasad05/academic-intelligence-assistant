# =====================================================================
# CAMPUSINTEL: PYTHON AUTO-DETECTOR & RUNNER
# Finds where Python is installed on your computer and launches the project
# =====================================================================

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  CAMPUSINTEL: SCANNING YOUR COMPUTER FOR EXISTING PYTHON INSTALLATION" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location -Path "D:\AgriNet\AWS\P3"

$foundPythons = [System.Collections.Generic.List[string]]::new()

# 1. Check where.exe
$wherePy = where.exe python 2>$null
if ($wherePy) {
    foreach ($w in $wherePy) {
        if (Test-Path $w) { $foundPythons.Add($w) }
    }
}

# 2. Check py launcher
$whereLauncher = where.exe py 2>$null
if ($whereLauncher) {
    foreach ($w in $whereLauncher) {
        if (Test-Path $w) { $foundPythons.Add($w) }
    }
}

# 3. Check Anaconda / Conda environments file
$condaEnvFile = "$env:USERPROFILE\.conda\environments.txt"
if (Test-Path $condaEnvFile) {
    $condaPaths = Get-Content $condaEnvFile
    foreach ($cp in $condaPaths) {
        $candidate = Join-Path $cp "python.exe"
        if (Test-Path $candidate) { $foundPythons.Add($candidate) }
    }
}

# 4. Check common installation directories
$commonRoots = @(
    "$env:LOCALAPPDATA\Programs\Python",
    "C:\Program Files\Python*",
    "C:\Python*",
    "D:\Python*",
    "$env:USERPROFILE\anaconda3",
    "$env:USERPROFILE\miniconda3",
    "C:\ProgramData\anaconda3",
    "C:\ProgramData\miniconda3"
)

foreach ($root in $commonRoots) {
    if (Test-Path $root) {
        $exes = Get-ChildItem -Path $root -Filter "python.exe" -Recurse -Depth 2 -ErrorAction SilentlyContinue
        foreach ($exe in $exes) {
            if (-not $foundPythons.Contains($exe.FullName)) {
                $foundPythons.Add($exe.FullName)
            }
        }
    }
}

# 5. Quick scan on C: and D: users and root for virtual environments
Write-Host "Scanning drives for existing python.exe or virtual environments..." -ForegroundColor Yellow
$extraScan = @("C:\Users\$env:USERNAME", "D:\AgriNet", "D:\")
foreach ($scanPath in $extraScan) {
    if (Test-Path $scanPath) {
        $results = Get-ChildItem -Path $scanPath -Filter "python.exe" -Recurse -Depth 4 -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -notmatch "WindowsApps" }
        foreach ($r in $results) {
            if (-not $foundPythons.Contains($r.FullName)) {
                $foundPythons.Add($r.FullName)
            }
        }
    }
}

Write-Host ""
if ($foundPythons.Count -eq 0) {
    Write-Host "[!] Could not automatically locate python.exe." -ForegroundColor Red
    Write-Host "Please type the folder path where you have Python installed below:" -ForegroundColor Yellow
    $manualPath = Read-Host "Enter path (e.g. C:\Users\YourName\...\python.exe)"
    if (Test-Path $manualPath) {
        $selectedPython = $manualPath
    } else {
        Write-Host "Path not found. Exiting." -ForegroundColor Red
        return
    }
} else {
    Write-Host "FOUND THE FOLLOWING PYTHON INSTALLATIONS ON YOUR SYSTEM:" -ForegroundColor Green
    for ($i = 0; $i -lt $foundPythons.Count; $i++) {
        Write-Host " [$i] $($foundPythons[$i])" -ForegroundColor White
    }
    Write-Host ""
    $choice = Read-Host "Select index to use [0-$($foundPythons.Count - 1)] (Default is 0)"
    if ([string]::IsNullOrWhiteSpace($choice)) { $choice = "0" }
    $selectedPython = $foundPythons[[int]$choice]
}

Write-Host ""
Write-Host "USING PYTHON: $selectedPython" -ForegroundColor Green
& $selectedPython --version
Write-Host ""

# Check if streamlit is already installed in this python environment
$hasStreamlit = & $selectedPython -m streamlit --version 2>$null
if ($hasStreamlit) {
    Write-Host "[OK] Streamlit is already installed in this Python environment!" -ForegroundColor Green
    Write-Host "Launching app directly..." -ForegroundColor Cyan
    & $selectedPython -m streamlit run app.py
} else {
    Write-Host "Setting up project dependencies in D:\AgriNet\AWS\P3 using this Python..." -ForegroundColor Yellow
    if (-not (Test-Path ".\venv\Scripts\Activate.ps1")) {
        Write-Host "Creating virtual environment in D:\AgriNet\AWS\P3\venv..." -ForegroundColor Yellow
        & $selectedPython -m venv venv
    }
    .\venv\Scripts\activate
    python -m pip install -r requirements.txt
    streamlit run app.py
}
