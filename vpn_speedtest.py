import json
import socket
import time
import concurrent.futures
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VPN_JSON_PATH = os.path.join(BASE_DIR, 'vpn.json')

def test_server_latency(server, timeout=2.5):
    """
    Menguji latensi TCP langsung ke port remote VPN server.
    Jika proto UDP, kita coba port TCP standar (443/995) atau remote port.
    """
    ip = server.get('ip')
    port = server.get('port', 443)
    proto = server.get('proto', 'tcp').lower()
    
    # Target port untuk socket probe
    target_ports = [port]
    if port != 443 and proto == 'tcp':
        target_ports.append(443)
    elif proto == 'udp':
        target_ports.extend([443, 995, 1194])

    best_rtt = None
    alive = False
    
    for p in target_ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        start_time = time.time()
        try:
            s.connect((ip, p))
            rtt_ms = round((time.time() - start_time) * 1000, 1)
            s.close()
            if best_rtt is None or rtt_ms < best_rtt:
                best_rtt = rtt_ms
                alive = True
                break
        except Exception:
            try:
                s.close()
            except:
                pass
                
    if alive and best_rtt is not None:
        # Hitung skor kualitas gabungan: Bandwidth tinggi + RTT rendah
        speed = server.get('speed_mbps', 0)
        # Quality score formula: (Speed / (RTT / 10))
        quality_score = round((speed * 10) / (best_rtt + 1), 2)
        return {
            "status": "online",
            "real_ping_ms": best_rtt,
            "quality_score": quality_score,
            "last_tested": datetime.now().isoformat()
        }
    else:
        return {
            "status": "offline",
            "real_ping_ms": None,
            "quality_score": 0,
            "last_tested": datetime.now().isoformat()
        }

def run_speedtest_benchmark(max_workers=25):
    if not os.path.exists(VPN_JSON_PATH):
        raise FileNotFoundError(f"File {VPN_JSON_PATH} tidak ditemukan! Jalankan vpn_fetcher.py terlebih dahulu.")
        
    with open(VPN_JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    servers = data.get('servers', [])
    print(f"Memulai Speed & Latency Benchmark untuk {len(servers)} server VPN (Concurrency: {max_workers})...")
    
    start_total = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_server = {executor.submit(test_server_latency, s): s for s in servers}
        completed = 0
        for future in concurrent.futures.as_completed(future_to_server):
            s = future_to_server[future]
            try:
                res = future.result()
                s.update(res)
            except Exception as e:
                s['status'] = 'error'
                s['real_ping_ms'] = None
                s['quality_score'] = 0
                s['last_tested'] = datetime.now().isoformat()
            completed += 1
            if completed % 20 == 0 or completed == len(servers):
                print(f"  Progres pengujian: {completed}/{len(servers)} server selesai dievaluasi...")

    duration = round(time.time() - start_total, 2)
    
    # Pisahkan server online & offline
    online_servers = [s for s in servers if s.get('status') == 'online']
    offline_servers = [s for s in servers if s.get('status') != 'online']
    
    # Urutkan server online berdasarkan quality_score tertinggi (kecepatan tinggi + ping rendah)
    online_servers.sort(key=lambda x: (x['quality_score'], -x['real_ping_ms']), reverse=True)
    
    # Gabungkan kembali
    final_servers = online_servers + offline_servers
    
    data['metadata']['last_benchmark'] = datetime.now().isoformat()
    data['metadata']['benchmark_duration_sec'] = duration
    data['metadata']['online_count'] = len(online_servers)
    data['metadata']['offline_count'] = len(offline_servers)
    data['servers'] = final_servers
    
    with open(VPN_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print("\n" + "="*50)
    print(f"HASIL BENCHMARK SELESAI ({duration} detik):")
    print(f"  - Total Server Diuji : {len(servers)}")
    print(f"  - Server ONLINE Aktif: {len(online_servers)}")
    print(f"  - Server OFFLINE     : {len(offline_servers)}")
    print("="*50)
    
    print("\nTOP 10 SERVER TERBAIK (HIGHEST QUALITY SCORE):")
    for i, s in enumerate(online_servers[:10]):
        print(f"  {i+1:2d}. [{s['country_code']}] {s['country']:<18} | IP: {s['ip']:<15}:{s['port']} | Latensi: {s['real_ping_ms']:>5.1f} ms | Speed: {s['speed_mbps']:>7.2f} Mbps | Skor: {s['quality_score']}")
    print("="*50)
    return data

if __name__ == "__main__":
    run_speedtest_benchmark()
