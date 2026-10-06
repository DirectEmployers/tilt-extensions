#!/usr/bin/env bash
: "${PIP_UPLOADED_PRIOR_TO:=P5D}"
cd "$(dirname "$(dirname "$0")")" || exit

# Prepare virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade 'pip>=26.1'

# Install extension requirements
if ! (pip freeze | grep -q boto3); then
  echo "Installing extension requirements..."
  pip install --uploaded-prior-to "${PIP_UPLOADED_PRIOR_TO}" -U boto3
  echo "Extension requirements have been installed."
fi

# Run
python3 src/main.py "$1" "$2"
