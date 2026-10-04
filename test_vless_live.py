import yaml
import subprocess
import time
import urllib.request
import os

url = "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub"
# test hysteria2 and vless nodes from pawdroid
import base64
with urllib.request.urlopen(url, timeout=10) as r:
    raw = r.read().decode('utf-8', errors='ignore')
try:
    decoded = base64.b64decode(raw).decode('utf-8', errors='ignore')
except:
    decoded = raw

lines = [l.strip() for l in decoded.splitlines() if l.strip()]
print(f"Total lines: {len(lines)}")

import sys
sys.path.append('/mnt/d/dev_vpn')
from test_vless_parse import parse_vless

vless_nodes = [l for l in lines if l.startswith('vless://')]
print(f"Total vless nodes: {len(vless_nodes)}")

for idx, link in enumerate(vless_nodes):
    p = parse_vless(link)
    name = p['name']
    
    test_cfg = {
        'port': 10808,
        'mode': 'global',
        'log-level': 'silent',
        'proxies': [p],
        'proxy-groups': [{'name': 'GLOBAL', 'type': 'select', 'proxies': [name]}],
        'rules': ['MATCH,GLOBAL']
    }
    with open('/tmp/test_vless_live.yaml', 'w') as f:
        yaml.dump(test_cfg, f)
        
    proc = subprocess.Popen(['/mnt/d/dev_vpn/mihomo', '-f', '/tmp/test_vless_live.yaml'],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)
    
    ip_out = None
    t0 = time.time()
    try:
        req_ip = urllib.request.Request('https://api.ipify.org', headers={'User-Agent': 'Mozilla/5.0'})
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({'http': 'http://127.0.0.1:10808', 'https': 'http://127.0.0.1:10808'}))
        with opener.open(req_ip, timeout=5) as resp:
            ip_out = resp.read().decode('utf-8').strip()
    except Exception as e:
        pass
        
    proc.terminate()
    try:
        proc.wait(timeout=1)
    except:
        proc.kill()
        
    if ip_out and ip_out != '103.165.60.14':
        rtt = round((time.time() - t0) * 1000)
        print(f"  [{idx+1}] SUCCESS EXIT IP: {ip_out} (RTT: {rtt} ms) -> {name}")
    else:
        print(f"  [{idx+1}] Fail: {name}")
