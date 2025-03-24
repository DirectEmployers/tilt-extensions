#!/usr/bin/env bash
cd "$(dirname "$(dirname "$0")")" || exit

# Prepare virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install extension requirements
if ! (pip freeze | grep -q boto3); then
  echo "Installing extension requirements..."
  pip install -U boto3
  echo "Extension requirements have been installed."
fi

# Run
python3 src/main.py "$1" "$2"
