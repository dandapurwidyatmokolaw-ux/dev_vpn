import yaml
import subprocess
import time
import urllib.request
import json
import os
from datetime import datetime

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
VPN_JSON_PATH = os.path.join(OUTPUT_DIR, 'vpn.json')
MIHOMO_BIN = os.path.join(OUTPUT_DIR, 'mihomo')

# Sumber Node Clash / V2Ray / Shadowsocks / Trojan harian yang aktif
FEED_URLS = [
    "https://raw.githubusercontent.com/zhaoligui0512/free-nodes/main/free-nodes.yaml",
    "https://raw.githubusercontent.com/zhuhaiuk/free-nodes/main/clash_config.yaml"
]

def fetch_and_test_nodes():
    print("Mengambil daftar node proxy VPN aktif dari feed terpercaya...")
    all_proxies = []
    seen_servers = set()

    for url in FEED_URLS:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=12) as r:
                cfg = yaml.safe_load(r.read().decode('utf-8'))
                for p in cfg.get('proxies', []):
                    srv = p.get('server')
                    port = p.get('port')
                    key = f"{srv}:{port}"
                    if srv and key not in seen_servers:
                        seen_servers.add(key)
                        all_proxies.append(p)
        except Exception as e:
            print(f"Error fetching {url}: {e}")

    print(f"Total kandidat server proxy ditemukan: {len(all_proxies)}")
    
    # Deteksi negara dari nama / server
    def detect_country(name):
        n = name.upper()
        if any(x in n for x in ['JP', '日本', 'TOKYO', 'JAPAN']):
            return 'Japan', 'JP'
        elif any(x in n for x in ['SG', '新加坡', 'SINGAPORE']):
            return 'Singapore', 'SG'
        elif any(x in n for x in ['US', '美国', 'UNITED STATES', 'AMERICA']):
            return 'United States', 'US'
        elif any(x in n for x in ['KR', '韩国', 'KOREA', 'INCHEON']):
            return 'Korea Republic of', 'KR'
        elif any(x in n for x in ['TW', '台湾', 'TAIWAN']):
            return 'Taiwan', 'TW'
        elif any(x in n for x in ['HK', '香港', 'HONG KONG']):
            return 'Hong Kong', 'HK'
        elif any(x in n for x in ['PH', '马尼拉', 'PHILIPPINES']):
            return 'Philippines', 'PH'
        elif any(x in n for x in ['MY', '吉隆坡', 'MALAYSIA']):
            return 'Malaysia', 'MY'
        elif any(x in n for x in ['CA', '加拿大', 'CANADA']):
            return 'Canada', 'CA'
        elif any(x in n for x in ['NL', '荷兰', 'NETHERLANDS']):
            return 'Netherlands', 'NL'
        elif any(x in n for x in ['DE', '德国', 'GERMANY']):
            return 'Germany', 'DE'
        elif any(x in n for x in ['GB', 'UK', '英国', 'UNITED KINGDOM']):
            return 'United Kingdom', 'GB'
        else:
            return 'Global Proxy', 'UN'

    # Uji konektivitas HTTP nyata melalui Mihomo Engine
    print("Menguji koneksi nyata & mendeteksi Exit IP untuk setiap server...")
    verified_servers = []

    for idx, p in enumerate(all_proxies):
        name = p['name']
        ptype = p['type']
        server_host = p['server']
        server_port = p['port']
        country, country_code = detect_country(name)
        
        # Test config
        test_cfg = {
            'port': 10818, # port sementara probe
            'mode': 'global',
            'log-level': 'silent',
            'proxies': [p],
            'proxy-groups': [{'name': 'GLOBAL', 'type': 'select', 'proxies': [name]}],
            'rules': ['MATCH,GLOBAL']
        }
        with open('/tmp/probe_vpn.yaml', 'w') as f:
            yaml.dump(test_cfg, f)

        proc = subprocess.Popen([MIHOMO_BIN, '-f', '/tmp/probe_vpn.yaml'],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.8)

        ip_out = None
        t0 = time.time()
        try:
            req_ip = urllib.request.Request('https://api.ipify.org', headers={'User-Agent': 'Mozilla/5.0'})
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({'http': 'http://127.0.0.1:10818', 'https': 'http://127.0.0.1:10818'}))
            with opener.open(req_ip, timeout=3.5) as resp:
                ip_out = resp.read().decode('utf-8').strip()
        except:
            pass

        proc.terminate()
        try:
            proc.wait(timeout=1)
        except:
            proc.kill()

        if ip_out and ip_out != '103.165.60.14':
            rtt_ms = round((time.time() - t0) * 1000, 1)
            print(f"  [{len(verified_servers)+1:2d}] ONLINE: [{country_code}] {country} ({ptype}) -> Exit IP: {ip_out} | Latensi: {rtt_ms} ms")
            
            srv_obj = {
                "id": f"vpn_{country_code.lower()}_{len(verified_servers)+1}",
                "name": name,
                "type": ptype,
                "server": server_host,
                "port": server_port,
                "country": country,
                "country_code": country_code,
                "exit_ip": ip_out,
                "real_ping_ms": rtt_ms,
                "status": "online",
                "clash_proxy": p,
                "last_tested": datetime.now().isoformat()
            }
            verified_servers.append(srv_obj)
        else:
            pass

    # Urutkan berdasarkan latensi terendah
    verified_servers.sort(key=lambda x: x['real_ping_ms'])

    vpn_data = {
        "metadata": {
            "total_servers": len(verified_servers),
            "generated_at": datetime.now().isoformat(),
            "source": "Verified Dedicated Inbound VPN Feeds"
        },
        "servers": verified_servers
    }

    with open(VPN_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(vpn_data, f, indent=2, ensure_ascii=False)

    print("\n" + "="*50)
    print(f"PROSES SELESAI:")
    print(f"  - Total Server Terverifikasi Tembus Internet: {len(verified_servers)}")
    print(f"  - Database Disimpan di: {VPN_JSON_PATH}")
    print("="*50)

if __name__ == "__main__":
    fetch_and_test_nodes()
