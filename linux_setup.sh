#!/usr/bin/env bash

# Exit on error
set -e

# --- Check Python version ---
PY_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')

if dpkg --compare-versions "$PY_VERSION" lt "3.11"; then
    echo "Python version is $PY_VERSION, but 3.11 or higher is required."
    exit 1
fi

echo "Python version $PY_VERSION OK"

# --- Install python3-venv ---
echo "Installing python3-venv..."
sudo apt update
sudo apt install -y python3-venv

# --- Create virtual environment ---
echo "Creating virtual environment..."
python3 -m venv venv

# --- Activate virtual environment ---
echo "Activating virtual environment..."
# shellcheck disable=SC1091
source venv/bin/activate

# --- Install requirements ---
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "No requirements.txt found in the current directory."
fi

echo "Setup complete."
