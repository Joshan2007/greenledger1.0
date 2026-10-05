$root = Split-Path -Parent $MyInvocation.MyCommand.Path

function Get-PythonCommand {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) { return "python" }

    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) { return "py" }

    $candidates = @(
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
        "C:\Program Files\Python312\python.exe",
        "C:\Program Files\Python311\python.exe",
        "C:\Program Files\Python310\python.exe"
    )

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) { return $candidate }
    }

    return $null
}

$pythonCmd = Get-PythonCommand
if (-not $pythonCmd) {
    Write-Host "Python was not found. Install Python 3.10+ and enable 'Add python.exe to PATH', then run this again." -ForegroundColor Red
    exit 1
}

Start-Process powershell -WorkingDirectory (Join-Path $root "agent") -ArgumentList @(
    "-NoExit",
    "-Command",
    "`"$pythonCmd`" api.py"
)

Start-Process powershell -WorkingDirectory (Join-Path $root "backend") -ArgumentList @(
    "-NoExit",
    "-Command",
    "`"$pythonCmd`" main.py"
)

Start-Process powershell -WorkingDirectory (Join-Path $root "frontend") -ArgumentList @(
    "-NoExit",
    "-Command",
    "npm run dev"
)

Write-Host "GreenLedger services are starting in separate PowerShell windows."
Write-Host "Dashboard: http://localhost:3001"
Write-Host "Optimize page: http://localhost:3001/optimize"
