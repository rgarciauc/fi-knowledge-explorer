#!/usr/bin/env sh
set -eu

mkdir -p logs/containers
timestamp="$(date '+%Y%m%d-%H%M%S')"
logfile="logs/containers/docker-compose-${timestamp}.log"

echo "Capturing all container stdout/stderr to ${logfile}"
echo "Press Ctrl+C to stop capture. Services continue running."
docker compose logs --tail=200 -f 2>&1 | tee -a "${logfile}"
