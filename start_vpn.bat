@echo off
title Free VPN Manager ^& Dashboard
color 0b

echo ============================================================
echo   MENJALANKAN FREE VPN GATEWAY ^& WEB DASHBOARD
echo ============================================================
echo.

:: 1. Ambil IP WSL saat ini
for /f "tokens=*" %%i in ('wsl -u root hostname -I') do set RAW_WSL_IP=%%i
for %%a in (%RAW_WSL_IP%) do (
    set WSL_IP=%%a
    goto :ip_done
)
:ip_done

echo [*] WSL IP Terdeteksi : %WSL_IP%

:: 2. Verifikasi portproxy Windows
echo [*] Memeriksa Port Forwarding Windows [127.0.0.1:10808 dan 10809]...
netsh interface portproxy show v4tov4 | findstr /C:"%WSL_IP%" >nul 2>&1
if %errorlevel% equ 0 goto portproxy_ready

echo [*] Portproxy perlu diperbarui ke %WSL_IP%...
netsh interface portproxy add v4tov4 listenaddress=127.0.0.1 listenport=10808 connectaddress=%WSL_IP% connectport=10808 >nul 2>&1
netsh interface portproxy add v4tov4 listenaddress=127.0.0.1 listenport=10809 connectaddress=%WSL_IP% connectport=10809 >nul 2>&1

netsh interface portproxy show v4tov4 | findstr /C:"%WSL_IP%" >nul 2>&1
if %errorlevel% equ 0 goto portproxy_ready

echo [*] Meminta izin Administrator untuk port forwarding...
powershell.exe -NoProfile -Command "Start-Process powershell -Verb RunAs -ArgumentList '-Command netsh interface portproxy add v4tov4 listenaddress=127.0.0.1 listenport=10808 connectaddress=%WSL_IP% connectport=10808; netsh interface portproxy add v4tov4 listenaddress=127.0.0.1 listenport=10809 connectaddress=%WSL_IP% connectport=10809' -Wait"

:portproxy_ready
echo [*] Portproxy Windows siap [IP: %WSL_IP%].

:: 3. Jalankan service di WSL
echo [*] Memulai VPN Server Service di WSL...
wsl.exe -u danda /mnt/d/dev_vpn/run_vpn.sh

:: Tunggu 2 detik
ping -n 3 127.0.0.1 >nul

:: 4. Buka Web Dashboard di browser default Windows
echo [*] Membuka Web Dashboard di browser...
start http://localhost:8088

echo.
echo ============================================================
echo   LAYANAN BERHASIL DIAKTIFKAN!
echo   - Web Dashboard : http://localhost:8088
echo   - Proxy Firefox : 127.0.0.1:10808 [HTTP] / 10809 [SOCKS5]
echo ============================================================
echo.
ping -n 4 127.0.0.1 >nul
exit
