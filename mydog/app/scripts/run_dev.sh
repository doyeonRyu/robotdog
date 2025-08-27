#!/usr/bin/env bash
set -e
python -m venv .venv || true
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
export SECRET_TOKEN=${SECRET_TOKEN:-000000}
export HOST=0.0.0.0
export PORT=8000
python -m app.main
