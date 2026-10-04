import yaml
import subprocess
import time
import urllib.request
import json
import base64

url = "https://raw.githubusercontent.com/Barabama/FreeNodes/master/nodes/merged.txt"
with urllib.request.urlopen(url, timeout=10) as r:
    lines = [l.strip() for l in r.read().decode('utf-8', errors='ignore').splitlines() if l.strip()]

import sys
sys.path.append('/mnt/d/dev_vpn')
from test_barabama import parse_vmess

working_nodes = []

for idx, link in enumerate(lines[:25]):
    if not link.startswith('vmess://'):
        continue
    p = parse_vmess(link)
    if not p:
        continue
        
    p['name'] = f"node-{idx+1}"
    test_cfg = {
        'port': 10808,
        'mode': 'global',
        'log-level': 'silent',
        'proxies': [p],
        'proxy-groups': [{'name': 'GLOBAL', 'type': 'select', 'proxies': [p['name']]}],
        'rules': ['MATCH,GLOBAL']
    }
    with open('/tmp/test_barabama_node.yaml', 'w') as f:
        yaml.dump(test_cfg, f)
        
    proc = subprocess.Popen(['/mnt/d/dev_vpn/mihomo', '-f', '/tmp/test_barabama_node.yaml'],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    
    ip_out = None
    t0 = time.time()
    try:
        req_ip = urllib.request.Request('https://api.ipify.org', headers={'User-Agent': 'Mozilla/5.0'})
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({'http': 'http://127.0.0.1:10808', 'https': 'http://127.0.0.1:10808'}))
        with opener.open(req_ip, timeout=3) as resp:
            ip_out = resp.read().decode('utf-8').strip()
    except:
        pass
        
    proc.terminate()
    try:
        proc.wait(timeout=1)
    except:
        proc.kill()
        
    if ip_out and ip_out != '103.165.60.14':
        rtt = round((time.time() - t0) * 1000)
        print(f"  [{idx+1}] SUCCESS: Exit IP: {ip_out} (RTT: {rtt} ms) -> Server: {p['server']}:{p['port']}")
        working_nodes.append((p, ip_out, rtt))
    else:
        print(f"  [{idx+1}] Fail: {p['server']}")
        
    if len(working_nodes) >= 3:
        break

print(f"\nTotal working: {len(working_nodes)}")
