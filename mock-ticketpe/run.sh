#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
else
  source .venv/bin/activate
fi

echo "Mock TicketPE → http://127.0.0.1:8090/api/v1/events?city=Recife"
exec uvicorn main:app --reload --host 0.0.0.0 --port 8090
