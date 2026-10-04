import yaml
import subprocess
import time
import urllib.request
import os

with open('/mnt/d/dev_vpn/active_clash.yaml', 'r') as f:
    cfg = yaml.safe_load(f)

proxies = cfg.get('proxies', [])
print("Testing proxies in active_clash.yaml:", len(proxies))

# We must ensure the proxy group routes through the proxy, not DIRECT!
for idx, p in enumerate(proxies):
    name = p['name']
    ptype = p['type']
    
    test_cfg = {
        'port': 10808,
        'mode': 'global',
        'log-level': 'silent',
        'proxies': [p],
        'proxy-groups': [
            {
                'name': 'GLOBAL',
                'type': 'select',
                'proxies': [name]
            }
        ],
        'rules': [
            'MATCH,GLOBAL'
        ]
    }
    with open('/tmp/test_single_proxy.yaml', 'w') as f:
        yaml.dump(test_cfg, f)
        
    proc = subprocess.Popen(['/mnt/d/dev_vpn/mihomo', '-f', '/tmp/test_single_proxy.yaml'],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    
    ip_out = None
    t0 = time.time()
    try:
        req_ip = urllib.request.Request('https://api.ipify.org', headers={'User-Agent': 'Mozilla/5.0'})
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({'http': 'http://127.0.0.1:10808', 'https': 'http://127.0.0.1:10808'}))
        with opener.open(req_ip, timeout=4) as resp:
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
        print(f"  [{idx+1}] *** SUCCESS CHANGED IP ***: {name} ({ptype}) -> Exit IP: {ip_out} (RTT: {rtt} ms)")
    else:
        print(f"  [{idx+1}] Fail or Direct ({ip_out}): {name}")
