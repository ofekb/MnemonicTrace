#!/bin/bash

echo "[INFO] Starting Wallet Checker installation..."

# Step 1: Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed. Please install it first."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "[INFO] Detected Python version: $PYTHON_VERSION"

# Step 2: Create virtual environment
echo "[INFO] Creating virtual environment..."
python3 -m venv .venv

# Step 3: Activate virtual environment
source .venv/bin/activate

# Step 4: Check for Rust (needed by bip_utils)
if ! command -v cargo &> /dev/null; then
    echo "[INFO] Rust not found. Installing Rust (required for bip_utils)..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source $HOME/.cargo/env
else
    echo "[INFO] Rust is already installed."
fi

# Step 5: Install Python dependencies
echo "[INFO] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 6: Run the application
echo "[INFO] Launching Wallet Checker..."
python interactive_main.py
