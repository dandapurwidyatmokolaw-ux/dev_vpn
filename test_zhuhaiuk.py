import yaml
import subprocess
import time
import urllib.request
import os

url = "https://raw.githubusercontent.com/zhuhaiuk/free-nodes/main/clash_config.yaml"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10) as r:
    cfg = yaml.safe_load(r.read().decode('utf-8'))

proxies = cfg.get('proxies', [])
print(f"Total proxies in zhuhaiuk: {len(proxies)}")

# Filter out direct / reject
candidate_proxies = [p for p in proxies if p.get('server')]

# Test top 15 proxies one by one
working_nodes = []

for idx, p in enumerate(candidate_proxies[:25]):
    name = p['name']
    ptype = p['type']
    server = p['server']
    port = p['port']
    
    test_cfg = {
        'port': 10808,
        'mode': 'global',
        'log-level': 'silent',
        'proxies': [p]
    }
    with open('/tmp/test_node.yaml', 'w') as f:
        yaml.dump(test_cfg, f)
        
    proc = subprocess.Popen(['/mnt/d/dev_vpn/mihomo', '-f', '/tmp/test_node.yaml'],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    
    # test curl
    ip_out = None
    t0 = time.time()
    try:
        req_ip = urllib.request.Request('https://api.ipify.org', headers={'User-Agent': 'Mozilla/5.0'})
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({'http': 'http://127.0.0.1:10808', 'https': 'http://127.0.0.1:10808'}))
        with opener.open(req_ip, timeout=3) as resp:
            ip_out = resp.read().decode('utf-8').strip()
    except Exception as e:
        pass
        
    proc.terminate()
    try:
        proc.wait(timeout=1)
    except:
        proc.kill()
        
    if ip_out:
        rtt = round((time.time() - t0) * 1000)
        print(f"  [{idx+1}] SUCCESS: {name} ({ptype} @ {server}:{port}) -> Exit IP: {ip_out} (RTT: {rtt} ms)")
        working_nodes.append((p, ip_out, rtt))
    else:
        print(f"  [{idx+1}] Fail: {name} ({ptype})")
        
    if len(working_nodes) >= 5:
        break

print(f"\nTotal working nodes verified: {len(working_nodes)}")
