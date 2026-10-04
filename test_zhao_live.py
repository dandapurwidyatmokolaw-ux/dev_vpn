import yaml
import subprocess
import time
import urllib.request
import os

url = "https://raw.githubusercontent.com/zhaoligui0512/free-nodes/main/free-nodes.yaml"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10) as r:
    cfg = yaml.safe_load(r.read().decode('utf-8'))

proxies = cfg.get('proxies', [])
print(f"Total proxies in zhaoligui0512: {len(proxies)}")

working_nodes = []

for idx, p in enumerate(proxies[:25]):
    name = p['name']
    ptype = p['type']
    
    test_cfg = {
        'port': 10808,
        'mode': 'global',
        'log-level': 'silent',
        'proxies': [p],
        'proxy-groups': [{'name': 'GLOBAL', 'type': 'select', 'proxies': [name]}],
        'rules': ['MATCH,GLOBAL']
    }
    with open('/tmp/test_zhao_node.yaml', 'w') as f:
        yaml.dump(test_cfg, f)
        
    proc = subprocess.Popen(['/mnt/d/dev_vpn/mihomo', '-f', '/tmp/test_zhao_node.yaml'],
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
        print(f"  [{idx+1}] *** SUCCESS EXIT IP: {ip_out} (RTT: {rtt} ms) -> {name} ({ptype})")
        working_nodes.append((p, ip_out, rtt))
    else:
        print(f"  [{idx+1}] Fail: {name} ({ptype})")

print(f"\nTotal working nodes verified: {len(working_nodes)}")
