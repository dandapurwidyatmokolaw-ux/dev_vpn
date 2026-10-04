import os
import json
import time
import threading
import urllib.request
import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from vpn_controller import VPNController
from vpn_fetcher_v2 import fetch_and_test_nodes

DASHBOARD_PORT = 8088
controller = VPNController()
auto_failover_enabled = True
failover_thread = None

# Background monitor untuk Auto-Failover
def background_failover_watcher():
    global auto_failover_enabled
    consecutive_failures = 0
    while True:
        try:
            if controller.process and controller.current_server and auto_failover_enabled:
                chk = controller.health_check(timeout=3)
                if chk['success']:
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    print(f"[WATCHER] Connection check failed ({consecutive_failures}/2)")
                    if consecutive_failures >= 2:
                        print("[WATCHER] Triggering Auto-Failover!")
                        controller.failover_next()
                        consecutive_failures = 0
            else:
                consecutive_failures = 0
        except Exception as e:
            pass
        time.sleep(5)

class VPNRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == '/api/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            is_connected = controller.current_server is not None
            current = controller.current_server
            
            resp = {
                "connected": is_connected,
                "current_server": current,
                "proxy_port": 10808,
                "socks_port": 10809,
                "auto_failover": auto_failover_enabled,
                "total_servers": len(controller.servers)
            }
            self.wfile.write(json.dumps(resp).encode('utf-8'))
            return

        elif path == '/api/servers':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            controller.load_servers()
            self.wfile.write(json.dumps(controller.servers).encode('utf-8'))
            return

        elif path == '/' or path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            with open(os.path.join(BASE_DIR, 'dashboard.html'), 'rb') as f:
                self.wfile.write(f.read())
            return

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        global auto_failover_enabled
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else "{}"
        try:
            body = json.loads(post_data)
        except:
            body = {}

        if path == '/api/connect':
            server_id = body.get('server_id')
            target_server = None
            if server_id:
                target_server = next((s for s in controller.servers if s['id'] == server_id), None)
            else:
                # Quick connect best server
                if controller.servers:
                    target_server = controller.servers[0]

            if target_server:
                ok, res = controller.connect_server(target_server)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": ok, "details": res, "server": target_server}).encode('utf-8'))
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "Server not found"}).encode('utf-8'))
            return

        elif path == '/api/disconnect':
            controller.disconnect()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}).encode('utf-8'))
            return

        elif path == '/api/failover':
            ok = controller.failover_next()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": ok, "current_server": controller.current_server}).encode('utf-8'))
            return

        elif path == '/api/toggle_failover':
            auto_failover_enabled = not auto_failover_enabled
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"auto_failover": auto_failover_enabled}).encode('utf-8'))
            return

        elif path == '/api/refresh':
            # Background refresh
            threading.Thread(target=fetch_and_test_nodes, daemon=True).start()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "message": "Scraping & benchmark started"}).encode('utf-8'))
            return

        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    # Start failover watcher daemon
    t = threading.Thread(target=background_failover_watcher, daemon=True)
    t.start()
    
    server_address = ('0.0.0.0', DASHBOARD_PORT)
    httpd = HTTPServer(server_address, VPNRequestHandler)
    print(f"\n=======================================================")
    print(f"🚀 VPN DASHBOARD AKTIF: http://localhost:{DASHBOARD_PORT}")
    print(f"   (Bisa dibuka langsung di Browser Windows & WSL)")
    print(f"   Dedicated Proxy Port: 127.0.0.1:10808 (Khusus Firefox)")
    print(f"=======================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nMematikan server...")
        controller.disconnect()
        httpd.server_close()

if __name__ == '__main__':
    run_server()
