import urllib.request
import csv
import json
import base64
import re
import os
from datetime import datetime

OUTPUT_DIR = '/mnt/d/dev_vpn'
OUTPUT_JSON = os.path.join(OUTPUT_DIR, 'vpn.json')

# Sumber API publik VPN Gate (Tsukuba University Academic Project)
# Mirror API resmi
API_URLS = [
    "https://www.vpngate.net/api/iphone/",
    "http://www.vpngate.net/api/iphone/"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_raw_csv():
    for url in API_URLS:
        print(f"Mencoba mengambil data dari: {url} ...")
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = resp.read().decode('utf-8', errors='ignore')
                if "HostName" in data and "OpenVPN_ConfigData_Base64" in data:
                    print("Berhasil mengunduh data server VPN!")
                    return data
        except Exception as e:
            print(f"Gagal mengambil dari {url}: {e}")
    return None

def extract_remote_info(ovpn_text):
    """Mengekstrak host/IP, port, dan protokol dari teks config OVPN"""
    remote_match = re.search(r'^\s*remote\s+([^\s]+)\s+(\d+)', ovpn_text, re.M)
    proto_match = re.search(r'^\s*proto\s+([^\s]+)', ovpn_text, re.M)
    
    remote_host = remote_match.group(1) if remote_match else None
    remote_port = int(remote_match.group(2)) if remote_match else None
    proto = proto_match.group(1).lower() if proto_match else "udp"
    
    return remote_host, remote_port, proto

def run_scraper():
    raw_data = fetch_raw_csv()
    if not raw_data:
        raise RuntimeError("Gagal mengambil data dari seluruh mirror VPN Gate.")
        
    lines = [line.strip() for line in raw_data.splitlines() if line.strip() and not line.startswith('*')]
    reader = csv.DictReader(lines)
    
    servers = []
    seen_ips = set()
    
    for row in reader:
        ip = row.get('IP')
        hostname = row.get('HostName')
        country_long = row.get('CountryLong')
        country_short = row.get('CountryShort')
        speed_raw = row.get('Speed', '0')
        ping_raw = row.get('Ping', '999')
        score_raw = row.get('Score', '0')
        sessions_raw = row.get('NumVpnSessions', '0')
        uptime_raw = row.get('Uptime', '0')
        config_b64 = row.get('OpenVPN_ConfigData_Base64')
        
        if not ip or not config_b64:
            continue
            
        # Hindari duplikat IP
        if ip in seen_ips:
            continue
        seen_ips.add(ip)
        
        try:
            speed_bps = int(speed_raw) if speed_raw.isdigit() else 0
            ping_ms = int(ping_raw) if ping_raw.isdigit() else 999
            score = int(score_raw) if score_raw.isdigit() else 0
            sessions = int(sessions_raw) if sessions_raw.isdigit() else 0
        except:
            speed_bps, ping_ms, score, sessions = 0, 999, 0, 0
            
        speed_mbps = round(speed_bps / 1000000, 2)
        
        # Decode config untuk ekstraksi parameter port & proto
        try:
            ovpn_decoded = base64.b64decode(config_b64).decode('utf-8', errors='ignore')
            remote_host, remote_port, proto = extract_remote_info(ovpn_decoded)
        except Exception:
            remote_host, remote_port, proto = ip, 443, "tcp"
            ovpn_decoded = ""
            
        server_obj = {
            "id": f"vpn_{ip.replace('.', '_')}",
            "hostname": hostname,
            "ip": ip,
            "port": remote_port or 443,
            "proto": proto or "tcp",
            "country": country_long,
            "country_code": country_short.upper() if country_short else "UN",
            "speed_mbps": speed_mbps,
            "ping_ms": ping_ms,
            "score": score,
            "active_sessions": sessions,
            "operator": row.get('Operator', ''),
            "config_base64": config_b64,
            "status": "untested",
            "last_updated": datetime.now().isoformat()
        }
        servers.append(server_obj)
        
    # Urutkan berdasarkan Speed Mbps tertinggi
    servers.sort(key=lambda s: s['speed_mbps'], reverse=True)
    
    # Bungkus dalam struktur data final
    result = {
        "metadata": {
            "total_servers": len(servers),
            "generated_at": datetime.now().isoformat(),
            "source": "VPN Gate Project (University of Tsukuba)"
        },
        "servers": servers
    }
    
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        
    print(f"\nScraping selesai!")
    print(f"Total Server Terkumpul : {len(servers)}")
    print(f"File Output Tersimpan  : {OUTPUT_JSON}")
    
    # Tampilkan 5 Server Tercepat
    print("\nTop 5 Server Tercepat:")
    for i, s in enumerate(servers[:5]):
        print(f"  {i+1}. [{s['country_code']}] {s['country']} - IP: {s['ip']}:{s['port']} ({s['proto'].upper()}) | Speed: {s['speed_mbps']} Mbps | Ping: {s['ping_ms']} ms")
        
    # Distribusi Negara
    country_counts = {}
    for s in servers:
        c = s['country']
        country_counts[c] = country_counts.get(c, 0) + 1
    print("\nDistribusi Negara:")
    for c, cnt in sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:8]:
        print(f"  - {c}: {cnt} server")

if __name__ == "__main__":
    run_scraper()
