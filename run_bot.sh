#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "  First Bot - Procesador de Solicitudes"
echo "========================================"
echo ""
echo "Presiona Ctrl+C para detener el bot."
echo ""

trap '' SIGTSTP

while true; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Ejecutando bot..."
    .venv/bin/python -m src.first_bot.main
    echo ""
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Esperando 60 segundos para la próxima ejecución..."
    echo "(Click en la consola = pausa, Enter = reanuda)"
    sleep 60 &
    wait $!
done
