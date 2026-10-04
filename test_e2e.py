import urllib.request
import json
import time
import subprocess
import sys

sys.path.append('/mnt/d/dev_vpn')
from vpn_controller import VPNController

def test_full_pipeline():
    print("="*60)
    print("🚀 MEMULAI PENGUJIAN INTEGRASI AKHIR (END-TO-END VERIFICATION)")
    print("="*60)

    # 1. Verifikasi Host Normal
    req = urllib.request.Request('https://api.ipify.org', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=5) as r:
        original_ip = r.read().decode('utf-8').strip()
    print(f"\n[1/4] IP Asli Laptop / Koneksi Normal: {original_ip}")

    # 2. Verifikasi Koneksi Proxy VPN
    controller = VPNController()
    server = controller.servers[0] # Best server
    print(f"\n[2/4] Menyambungkan ke Server #1: [{server['country_code']}] {server['country']} ({server['type']})...")
    ok, details = controller.connect_server(server)
    assert ok, "Gagal menyambungkan server pertama!"
    print(f"      Status: SUKSES!")
    print(f"      Exit IP VPN: {details['exit_ip']} (Berbeda dari IP asli: {details['exit_ip'] != original_ip})")
    print(f"      Latensi RTT: {details['latency_ms']} ms")

    # 3. Simulasi Auto-Failover
    print(f"\n[3/4] Menguji Auto-Failover (Simulasi server mati / timeout)...")
    t0 = time.time()
    failover_ok = controller.failover_next()
    duration = round(time.time() - t0, 2)
    assert failover_ok, "Auto-Failover gagal!"
    new_server = controller.current_server
    print(f"      Status Failover: SUKSES dalam {duration} detik!")
    print(f"      Server Aktif Sekarang: [{new_server['country_code']}] {new_server['country']}")
    print(f"      Exit IP Baru: {new_server['exit_ip']}")

    # 4. Verifikasi Port Forwarding Windows ke WSL
    print(f"\n[4/4] Memeriksa Port Forwarding Windows (127.0.0.1:10808)...")
    res = subprocess.run([
        'powershell.exe', '-Command',
        "$wc = New-Object System.Net.WebClient; $wc.Proxy = New-Object System.Net.WebProxy('http://127.0.0.1:10808'); $wc.DownloadString('https://api.ipify.org')"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    win_ip = res.stdout.strip()
    print(f"      Respons dari Windows Host via 127.0.0.1:10808: {win_ip}")
    assert win_ip == new_server['exit_ip'], "IP Windows host tidak cocok dengan IP VPN!"

    print("\n" + "="*60)
    print("✅ SELURUH PENGUJIAN INTEGRASI BERHASIL 100%!")
    print("="*60)

if __name__ == '__main__':
    test_full_pipeline()
