#!/usr/bin/env bash
# Respaldo de SQLite (en caliente) y de los datos de Keycloak (con un corte de unos segundos).
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

keycloak_volume="$(volume_for_mount keycloak /opt/keycloak/data/h2)"
DEST="backups/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$DEST"

# 1) SQLite: copia consistente con la API de backup, sin detener la app
"${COMPOSE[@]}" exec -T app python - <<'PY'
import sqlite3
origen = sqlite3.connect("/data/db.sqlite3")
destino = sqlite3.connect("/data/backup.sqlite3")
with destino:
    origen.backup(destino)
destino.close()
origen.close()
PY
"${COMPOSE[@]}" cp app:/data/backup.sqlite3 "$DEST/db.sqlite3"
"${COMPOSE[@]}" exec -T app rm -f /data/backup.sqlite3

# 2) Keycloak (H2 en archivo): se detiene para copiar sin riesgo de corrupción
keycloak_stopped=0
restart_keycloak() {
  if [ "$keycloak_stopped" -eq 1 ]; then
    "${COMPOSE[@]}" start keycloak >/dev/null || {
      echo "No se pudo reiniciar Keycloak; iniciá el servicio manualmente." >&2
      return 1
    }
    keycloak_stopped=0
  fi
}
trap 'restart_keycloak || true' EXIT
"${COMPOSE[@]}" stop keycloak
keycloak_stopped=1
docker run --rm \
  -v "$keycloak_volume:/src:ro" \
  -v "$PWD/$DEST":/dst \
  alpine tar czf /dst/keycloak-data.tar.gz -C /src .
restart_keycloak
trap - EXIT

# 3) Retención: conservar los últimos 14 respaldos
ls -1d backups/*/ 2>/dev/null | head -n -14 | xargs -r rm -rf
echo "Respaldo creado en $DEST"
