# PowerShell Build Script for Epson Printer Configuration on Windows
$ErrorActionPreference = "Stop"

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Building Epson Printer Configuration for Windows" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

# 1. Check Python
$PythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonCmd) {
    Write-Error "Python is not installed or not in system PATH."
    exit 1
}

# 2. Dependencies
Write-Host "`n[1/4] Installing Python dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install pyinstaller pillow
python -m pip install -r requirements.txt

# 3. Icons
Write-Host "`n[2/4] Verifying assets & icons..." -ForegroundColor Yellow
if (-not (Test-Path "assets\app_icon.ico")) {
    python generate_icons.py
}

# 4. PyInstaller
Write-Host "`n[3/4] Running PyInstaller..." -ForegroundColor Yellow
python -m PyInstaller --noconfirm app_windows.spec

# 5. Packaging
Write-Host "`n[4/4] Creating ZIP package..." -ForegroundColor Yellow
if (Test-Path "dist\epson_print_conf.exe") {
    Compress-Archive -Path "dist\epson_print_conf.exe" -DestinationPath "dist\epson_print_conf-windows.zip" -Force
    Write-Host "`n✓ Build completed successfully!" -ForegroundColor Green
    Write-Host "  EXE: dist\epson_print_conf.exe" -ForegroundColor Green
    Write-Host "  ZIP: dist\epson_print_conf-windows.zip" -ForegroundColor Green
} else {
    Write-Error "Executable was not found in dist/."
}
