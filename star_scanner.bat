@echo off
title StarBT Script Setup and Launcher

echo ===================================================
echo   StarBT Installment Finder Launcher
echo ===================================================
echo.

:: 1. Check if Python is globally available
python --version >nul 2>&1
if %errorlevel% equ 0 goto :RUN_SCRIPT

:: 2. If global check fails, look for it in the standard local AppData path
set "LOCAL_PY=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
if exist "%LOCAL_PY%" (
    set "PY_CMD=%LOCAL_PY%"
    goto :INSTALL_DEPS
)

set "LOCAL_PY_DEFAULT=%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe"
if exist "%LOCAL_PY_DEFAULT%" (
    set "PY_CMD=%LOCAL_PY_DEFAULT%"
    goto :INSTALL_DEPS
)

:: 3. If Python is missing completely, download it
echo [!] Python is not detected on your system.
echo [*] Downloading Python Installer...
echo.

powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '%TEMP%\python_installer.exe'"

if not exist "%TEMP%\python_installer.exe" (
    echo [X] Error: Failed to download Python installer.
    pause
    exit /b
)

echo [*] Launching Python Installer...
echo [IMPORTANT] Please make sure to CHECK the box that says:
echo             "Add python.exe to PATH" at the bottom of the installer window!
echo.
"%TEMP%\python_installer.exe"
echo.
echo [*] If the installation finished successfully, please CLOSE this window
echo     and double-click star_scanner.bat again to run the script.
pause
exit /b

:RUN_SCRIPT
set "PY_CMD=python"

:INSTALL_DEPS
echo [OK] Python detected.
echo [*] Checking and installing required packages...
"%PY_CMD%" -m pip install --upgrade pip --quiet
"%PY_CMD%" -m pip install requests beautifulsoup4 --quiet
echo [OK] Dependencies ready.
echo.

:: Look for the script in the current directory
if not exist "star_scanner.py" (
    echo [X] Error: Cannot find 'star_scanner.py' in this folder.
    echo Please make sure this file is named 'star_scanner.bat' and placed
    echo in the exact same directory as your 'star_scanner.py' script.
    echo.
    pause
    exit /b
)

echo [*] Launching StarBT Scraper...
echo ---------------------------------------------------
"%PY_CMD%" star_scanner.py
echo ---------------------------------------------------
echo.
echo [*] Script finished executing.
pause
exit /b
