@echo off
echo [INFO] Starting Wallet Checker installation...

:: Step 1: Check Python
where python >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found. Please install Python 3.8 or newer from https://www.python.org/downloads/
    pause
    exit /b
)

:: Step 2: Create virtual environment
echo [INFO] Creating virtual environment...
python -m venv .venv

:: Step 3: Activate venv and install pip
call .venv\Scripts\activate

:: Step 4: Check for Rust
where cargo >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [INFO] Rust not found. Installing Rust...
    curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs -o rustup-init.exe
    rustup-init.exe -y
    set PATH=%USERPROFILE%\.cargo\bin;%PATH%
) ELSE (
    echo [INFO] Rust is already installed.
)

:: Step 5: Install Python dependencies
echo [INFO] Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

:: Step 6: Run the application
echo [INFO] Running Wallet Checker...
python interactive_main.py

pause
