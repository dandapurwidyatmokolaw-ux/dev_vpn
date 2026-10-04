import urllib.request
import base64
import json
import re
import csv
import sys
sys.path.append('/mnt/d/dev_vpn')
from test_vless_parse import parse_vless

def get_pawdroid_vless():
    url = "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as r:
        raw = r.read().decode('utf-8', errors='ignore')
    try:
        decoded = base64.b64decode(raw).decode('utf-8', errors='ignore')
    except:
        decoded = raw
    lines = [l.strip() for l in decoded.splitlines() if l.strip()]
    nodes = []
    for l in lines:
        if l.startswith('vless://'):
            node = parse_vless(l)
            if node:
                nodes.append(node)
    return nodes

nodes = get_pawdroid_vless()
print(f"Extracted {len(nodes)} VLESS nodes from Pawdroid.")
for n in nodes:
    print(f"  - [{n['type']}] {n['name']} -> {n['server']}:{n['port']}")
