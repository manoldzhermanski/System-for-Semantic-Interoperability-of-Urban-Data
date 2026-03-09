#!/usr/bin/env bash
set -euo pipefail

COMMAND=${1:-}

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

VENV_PATH="$ROOT_DIR/venv"
BROKER_URL="http://localhost:9090"

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
  echo "  ./automation.sh clear_all"
  exit 1
}

clear_all() {
  activate_venv
  docker system prune -a --volumes
}

activate_venv() {
  if [[ ! -f "$VENV_PATH/bin/activate" ]]; then
    echo "Virtualenv not found at $VENV_PATH"
    exit 1
  fi
  source "$VENV_PATH/bin/activate"
}

wait_for_scorpio() {
  echo "Waiting for Scorpio Broker..."
  for i in {1..60}; do
    if curl -sf "$BROKER_URL/q/health/ready" > /dev/null; then
      echo "Scorpio is ready!"
      return 0
    fi
    sleep 2
  done
  echo "Scorpio did not start in time"
  docker logs scorpio
  exit 1
}

gtfs_static_rebuild() {
  activate_venv

  docker compose up -d scorpio postgres
  wait_for_scorpio

  echo "Starting FastAPI backend..."
  uvicorn backend_api.main:app --reload &
  UVICORN_PID=$!

  echo "Waiting for FastAPI to start..."

  until curl -s http://localhost:8000/docs > /dev/null; do
    sleep 1
  done

  echo "FastAPI is up!"

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

start() {

    activate_venv

    echo "Starting Docker containers..."
    docker compose up -d scorpio postgres terriamap otp

    wait_for_scorpio

    echo "Starting FastAPI backend..."
    uvicorn backend_api.main:app --reload &
    UVICORN_PID=$!

    echo "Waiting for FastAPI to start..."

    until curl -s http://localhost:8000/docs > /dev/null; do
      sleep 1
    done

    echo "FastAPI is up!"
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
  wait_for_scorpio

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
  clear_all)
    clear_all
    ;;
  *)
    usage
    ;;
esac