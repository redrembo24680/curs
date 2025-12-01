#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT/web_flask"

PYTHON="python3"
if [ -x "$ROOT/venv/bin/python" ]; then
    PYTHON="$ROOT/venv/bin/python"
fi

$PYTHON -m pip install -r requirements.txt >/dev/null

export FLASK_APP=app.py
export API_BASE_URL="${API_BASE_URL:-http://localhost:8080/api}"

$PYTHON -m flask run --port 5000