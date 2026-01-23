#!/usr/bin/env bash
set -euo pipefail

COMMAND=${1:-}

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

VENV_PATH="$ROOT_DIR/venv"
ORION_URL="http://localhost:1026"

usage() {
  echo "Usage:"
  echo "  ./automation.sh start"
  echo "  ./automation.sh stop"
  echo "  ./automation.sh test"
  echo "  ./automation.sh load [gtfs] [pois]"
  exit 1
}

activate_venv() {
  if [[ ! -f "$VENV_PATH/bin/activate" ]]; then
    echo "Virtualenv not found at $VENV_PATH"
    exit 1
  fi
  source "$VENV_PATH/bin/activate"
}

wait_for_orion() {
  echo "Waiting for Orion-LD..."
  until curl -s "$ORION_URL/version" > /dev/null; do
    sleep 2
  done
}

start() {

    activate_venv

    echo "Starting Docker containers..."
    docker compose up -d

    wait_for_orion

    echo "Starting FastAPI backend..."
    uvicorn backend_api.main:app --reload
}

stop() {
  echo "Stopping Docker containers..."
  docker compose down
}

pytest() {
  echo "Running Unit tests..."
  activate_venv
  python -m pytest -vv
}

load() {
  shift

  if [[ $# -eq 0 ]]; then
    echo "Specify what to load: gtfs, pois"
    exit 1
  fi

  activate_venv

  echo "Starting Docker containers..."
  docker compose up -d
  
  wait_for_orion

  echo "Loading data: $*"
  python load_orion_ld_data.py "$@"
}

case "$COMMAND" in
  start)
    start
    ;;
  stop)
    stop
    ;;
  test)
    pytest
    ;;
  load)
    load "$@"
    ;;
  *)
    usage
    ;;
esac
