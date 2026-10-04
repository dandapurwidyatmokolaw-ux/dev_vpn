import json
import subprocess
import time
import urllib.request
import os
import signal
import yaml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VPN_JSON_PATH = os.path.join(BASE_DIR, 'vpn.json')
MIHOMO_BIN = os.path.join(BASE_DIR, 'mihomo')
RUNTIME_DIR = os.path.join(BASE_DIR, 'runtime')
PROXY_PORT = 10808
API_PORT = 9090

os.makedirs(RUNTIME_DIR, exist_ok=True)

class VPNController:
    def __init__(self):
        self.process = None
        self.current_server = None
        self.active_index = 0
        self.load_servers()
        
    def load_servers(self):
        with open(VPN_JSON_PATH, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.servers = self.data.get('servers', [])
        print(f"[CONTROLLER] Loaded {len(self.servers)} verified servers from vpn.json")
        
    def connect_server(self, server_obj):
        self.disconnect()
        name = server_obj['name']
        proxy_def = server_obj['clash_proxy']
        
        # Build clean config for Mihomo
        cfg = {
            'port': PROXY_PORT,
            'socks-port': PROXY_PORT + 1, # 10809
            'allow-lan': True,
            'mode': 'global',
            'log-level': 'warning',
            'external-controller': f'127.0.0.1:{API_PORT}',
            'proxies': [proxy_def],
            'proxy-groups': [
                {
                    'name': 'GLOBAL',
                    'type': 'select',
                    'proxies': [name]
                }
            ],
            'rules': ['MATCH,GLOBAL']
        }
        
        cfg_file = os.path.join(RUNTIME_DIR, 'active_runtime.yaml')
        with open(cfg_file, 'w', encoding='utf-8') as f:
            yaml.dump(cfg, f, allow_unicode=True)
            
        print(f"[CONTROLLER] Connecting to [{server_obj['country_code']}] {server_obj['country']} (IP: {server_obj['exit_ip']})...")
        self.process = subprocess.Popen([MIHOMO_BIN, '-f', cfg_file],
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1.2)
        
        # Verify connection
        check_res = self.health_check()
        if check_res['success']:
            self.current_server = server_obj
            print(f"[CONTROLLER] CONNECTED! Exit IP: {check_res['exit_ip']} (Ping: {check_res['latency_ms']} ms)")
            return True, check_res
        else:
            print(f"[CONTROLLER] FAILED to connect: {check_res.get('error')}")
            self.disconnect()
            return False, check_res
            
    def health_check(self, timeout=3.5):
        t0 = time.time()
        try:
            req = urllib.request.Request('https://api.ipify.org', headers={'User-Agent': 'Mozilla/5.0'})
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({
                'http': f'http://127.0.0.1:{PROXY_PORT}',
                'https': f'http://127.0.0.1:{PROXY_PORT}'
            }))
            with opener.open(req, timeout=timeout) as resp:
                ip_out = resp.read().decode('utf-8').strip()
                rtt = round((time.time() - t0) * 1000, 1)
                return {"success": True, "exit_ip": ip_out, "latency_ms": rtt}
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def failover_next(self):
        print("\n[AUTO-FAILOVER] Connection issue detected! Switching to next best server...")
        total = len(self.servers)
        for attempt in range(1, total):
            self.active_index = (self.active_index + 1) % total
            next_server = self.servers[self.active_index]
            print(f"[AUTO-FAILOVER] Attempting server #{self.active_index + 1}: [{next_server['country_code']}] {next_server['country']} ({next_server['exit_ip']})")
            ok, res = self.connect_server(next_server)
            if ok:
                print(f"[AUTO-FAILOVER] SUCCESS! Failover completed to {next_server['country']}.\n")
                return True
        print("[AUTO-FAILOVER] Error: None of the backup servers succeeded.")
        return False

    def disconnect(self):
        # Kill any running mihomo processes
        subprocess.run(['pkill', '-9', '-f', 'mihomo'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=1)
            except:
                try:
                    self.process.kill()
                except:
                    pass
            self.process = None
        self.current_server = None

if __name__ == "__main__":
    controller = VPNController()
    
    # 1. Connect to Top 1 (Singapore)
    server_1 = controller.servers[0]
    ok, res = controller.connect_server(server_1)
    
    # 2. Simulate Failover
    time.sleep(2)
    controller.failover_next()
    
    # 3. Clean disconnect
    time.sleep(2)
    controller.disconnect()
    print("[TEST] All tests completed cleanly.")
