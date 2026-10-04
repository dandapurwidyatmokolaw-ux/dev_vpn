#!/bin/bash
# Helper runner untuk stop VPN server di WSL
if command -v systemctl >/dev/null 2>&1; then
    systemctl --user stop dev-vpn.service 2>/dev/null || true
fi
pkill -f 'vpn_server.py' 2>/dev/null || true
pkill -9 -f 'mihomo' 2>/dev/null || true
