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
  echo "  ./automation.sh load gtfs sofia"
  echo "  ./automation.sh load gtfs helsinki"
  echo "  ./automation.sh load gtfs sofia helsinki"
  echo "  ./automation.sh load pois"
  echo "  ./automation.sh otp_build"
  echo "  ./automation.sh gtfs_static_rebuild"
  exit 1
}

activate_venv() {
  if [[ ! -f "$VENV_PATH/bin/activate" ]]; then
    echo "Virtualenv not found at $VENV_PATH"
    exit 1
  fi
  source "$VENV_PATH/bin/activate"
}

gtfs_static_rebuild() {
  activate_venv
  docker compose up -d orion mongo-db
  wait_for_orion

  echo "Rebuilding GTFS static data..."
  curl -X POST http://localhost:8000/api/gtfs_static/rebuild
}

otp_build() {
  
  activate_venv

  docker compose up otp-build

  echo "Waiting for otp-build to finish..."
  while true; do
    status=$(docker inspect -f '{{.State.Status}}' otp-build 2>/dev/null)
    if [ "$status" == "exited" ]; then
      echo "otp-build finished."
      break
    fi
    sleep 2
  done

  exit_code=$(docker inspect -f '{{.State.ExitCode}}' otp-build)
  if [ "$exit_code" -ne 0 ]; then
      echo "otp-build failed with code $exit_code"
      docker logs otp-build
      exit 1
  fi
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
    docker compose up -d orion mongo-db terriamap otp

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
  gtfs_static_rebuild)
    gtfs_static_rebuild
    ;;
  otp_build)
    otp_build "$@"
    ;;
  *)
    usage
    ;;
esac

