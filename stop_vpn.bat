@echo off
title Hentikan VPN Gateway
color 0c

echo Menghentikan seluruh proses VPN Server dan Mihomo di WSL...
wsl.exe -u danda /mnt/d/dev_vpn/stop_vpn.sh

echo Layanan VPN berhasil dihentikan.
ping -n 3 127.0.0.1 >nul
exit
