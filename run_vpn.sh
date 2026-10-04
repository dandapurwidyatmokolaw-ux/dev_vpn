#!/bin/bash
# Helper runner untuk start VPN server di WSL
if command -v systemctl >/dev/null 2>&1 && systemctl --user is-active --quiet dev-vpn.service; then
    echo "[WSL] dev-vpn.service is already active."
    exit 0
fi

if command -v systemctl >/dev/null 2>&1; then
    systemctl --user start dev-vpn.service 2>/dev/null && exit 0
fi

# Fallback background process
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if ! pgrep -f 'vpn_server.py' >/dev/null 2>&1; then
    nohup python3 "$SCRIPT_DIR/vpn_server.py" > "$SCRIPT_DIR/vpn_server.log" 2>&1 &
    sleep 1
fi
