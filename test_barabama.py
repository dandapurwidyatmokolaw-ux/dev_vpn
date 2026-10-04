import urllib.request
import base64
import json
import re

url = "https://raw.githubusercontent.com/Barabama/FreeNodes/master/nodes/merged.txt"
with urllib.request.urlopen(url, timeout=10) as r:
    lines = [l.strip() for l in r.read().decode('utf-8', errors='ignore').splitlines() if l.strip()]

print(f"Total nodes in Barabama: {len(lines)}")

def parse_vmess(link):
    try:
        raw = link[8:]
        decoded = base64.b64decode(raw + "==").decode('utf-8', errors='ignore')
        obj = json.loads(decoded)
        return {
            "name": obj.get('ps') or f"vmess-{obj.get('add')}",
            "type": "vmess",
            "server": obj.get('add'),
            "port": int(obj.get('port')),
            "uuid": obj.get('id'),
            "alterId": int(obj.get('aid', 0)),
            "cipher": obj.get('scy', 'auto'),
            "tls": obj.get('tls') == 'tls',
            "network": obj.get('net', 'tcp'),
            "servername": obj.get('sni') or obj.get('host'),
            "ws-opts": {
                "path": obj.get('path', '/'),
                "headers": {"Host": obj.get('host') or obj.get('add')}
            } if obj.get('net') == 'ws' else None
        }
    except Exception as e:
        return None

parsed = [parse_vmess(l) for l in lines[:10] if l.startswith('vmess://')]
print(f"Sample 1 parsed vmess:\n", json.dumps(parsed[0], indent=2))
