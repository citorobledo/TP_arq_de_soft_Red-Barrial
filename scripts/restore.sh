#!/usr/bin/env bash
# Uso: scripts/restore.sh backups/AAAAMMDD-HHMMSS
set -euo pipefail
cd "$(dirname "$0")/.."

if docker compose version >/dev/null 2>&1; then
  COMPOSE=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE=(docker-compose)
else
  echo "No se encontró Docker Compose (docker compose o docker-compose)." >&2
  exit 1
fi

volume_for_mount() {
  local service="$1"
  local destination="$2"
  local container_id
  local volume

  container_id="$("${COMPOSE[@]}" ps -q "$service")"
  if [ -z "$container_id" ]; then
    echo "El servicio '$service' no está iniciado. Iniciá los servicios con Compose y reintentá." >&2
    return 1
  fi

  volume="$(docker inspect --format \
    "{{range .Mounts}}{{if eq .Destination \"$destination\"}}{{.Name}}{{end}}{{end}}" \
    "$container_id")"
  if [ -z "$volume" ]; then
    echo "No se encontró un volumen Docker montado en '$destination' para '$service'." >&2
    return 1
  fi
  printf '%s\n' "$volume"
}

SRC="${1:?Uso: scripts/restore.sh backups/AAAAMMDD-HHMMSS}"
SRC="$(cd -- "$SRC" && pwd)" || { echo "No existe el directorio de respaldo indicado."; exit 1; }
[ -f "$SRC/db.sqlite3" ] || { echo "No existe $SRC/db.sqlite3"; exit 1; }

app_volume="$(volume_for_mount app /data)"
keycloak_volume="$(volume_for_mount keycloak /opt/keycloak/data/h2)"

read -r -p "Esto REEMPLAZA los datos actuales. Escribí 'si' para continuar: " ok
[ "$ok" = "si" ] || { echo "Cancelado."; exit 1; }

services_stopped=0
restart_services() {
  if [ "$services_stopped" -eq 1 ]; then
    "${COMPOSE[@]}" start app keycloak >/dev/null || {
      echo "No se pudieron reiniciar app y Keycloak; iniciá los servicios manualmente." >&2
      return 1
    }
    services_stopped=0
  fi
}
trap 'restart_services || true' EXIT
"${COMPOSE[@]}" stop app keycloak
services_stopped=1

docker run --rm \
  -v "$app_volume:/data" \
  -v "$SRC:/src:ro" \
  alpine sh -c 'cp /src/db.sqlite3 /data/db.sqlite3 && rm -f /data/db.sqlite3-wal /data/db.sqlite3-shm && chown 1000:1000 /data/db.sqlite3'

if [ -f "$SRC/keycloak-data.tar.gz" ]; then
  docker run --rm \
    -v "$keycloak_volume:/dst" \
    -v "$SRC:/src:ro" \
    alpine sh -c 'find /dst -mindepth 1 -maxdepth 1 -exec rm -rf -- {} + && tar xzf /src/keycloak-data.tar.gz -C /dst && chown -R 1000:0 /dst'
fi

"${COMPOSE[@]}" start app keycloak
services_stopped=0
trap - EXIT
"${COMPOSE[@]}" up -d
echo "Restauración completa desde $SRC"
