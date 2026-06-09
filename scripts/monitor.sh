#!/usr/bin/env bash
# Monitor de Ciclo AudioLabEditor — wrapper start/stop/status
# Uso: ./scripts/monitor.sh {start|stop|status|restart}

PIDFILE="/tmp/audioeditor-monitor.pid"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="${PYTHON:-python3}"

case "${1:-status}" in
    start)
        if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
            echo "Monitor ja esta rodando (pid $(cat "$PIDFILE"))."
            exit 1
        fi
        nohup "$PYTHON" "$SCRIPT_DIR/monitor.py" daemon --interval 300 \
            > /tmp/audioeditor-monitor.log 2>&1 &
        echo $! > "$PIDFILE"
        echo "Monitor iniciado (pid $!). Log: /tmp/audioeditor-monitor.log"
        ;;
    stop)
        if [ ! -f "$PIDFILE" ]; then
            echo "Monitor nao esta rodando."
            exit 0
        fi
        PID=$(cat "$PIDFILE")
        kill "$PID" 2>/dev/null && echo "Monitor parado (pid $PID)." || echo "Falha ao parar."
        rm -f "$PIDFILE"
        ;;
    status)
        if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
            echo "Monitor rodando (pid $(cat "$PIDFILE"))."
            "$PYTHON" "$SCRIPT_DIR/monitor.py" status
        else
            echo "Monitor parado."
            "$PYTHON" "$SCRIPT_DIR/monitor.py" status
        fi
        ;;
    restart)
        "$0" stop; sleep 1; "$0" start
        ;;
    *)
        echo "Uso: $0 {start|stop|status|restart}"
        exit 1
        ;;
esac
