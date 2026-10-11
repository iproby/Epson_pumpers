@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo   Building Epson Printer Configuration for Windows
echo ===================================================

cd /d "%~dp0"

:: 1. Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    pause
    exit /b 1
)

:: 2. Install dependencies
echo [1/4] Installing required packages...
python -m pip install --upgrade pip
python -m pip install pyinstaller pillow
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

:: 3. Generate icons if missing
echo [2/4] Verifying icons...
if not exist "assets\app_icon.ico" (
    python generate_icons.py
)

:: 4. Build standalone executable
echo [3/4] Running PyInstaller...
python -m PyInstaller --noconfirm app_windows.spec
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller build failed!
    pause
    exit /b 1
)

:: 5. Create zip package
echo [4/4] Creating ZIP package...
powershell -Command "Compress-Archive -Path dist\epson_print_conf.exe -DestinationPath dist\epson_print_conf-windows.zip -Force"

echo.
echo ===================================================
echo   Build Successful!
echo   Executable: dist\epson_print_conf.exe
echo   ZIP Archive: dist\epson_print_conf-windows.zip
echo ===================================================
pause
