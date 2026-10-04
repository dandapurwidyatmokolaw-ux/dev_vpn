import json
import base64
import yaml
import re

with open('/mnt/d/dev_vpn/vpn.json') as f:
    data = json.load(f)

server = data['servers'][0]
cfg = base64.b64decode(server['config_base64']).decode('utf-8', errors='ignore')

ca_match = re.search(r'<ca>(.*?)</ca>', cfg, re.DOTALL)
cert_match = re.search(r'<cert>(.*?)</cert>', cfg, re.DOTALL)
key_match = re.search(r'<key>(.*?)</key>', cfg, re.DOTALL)

ca_str = ca_match.group(1).strip() if ca_match else ""
cert_str = cert_match.group(1).strip() if cert_match else ""
key_str = key_match.group(1).strip() if key_match else ""

clash_proxy = {
    "name": f"vpn-{server['country_code']}-{server['ip']}",
    "type": "openvpn",
    "server": server['ip'],
    "port": server['port'],
    "protocol": server['proto'],
    "cipher": "AES-128-CBC",
    "auth": "SHA1",
    "ca": ca_str,
    "certificate": cert_str,
    "private-key": key_str
}

clash_cfg = {
    "port": 10808,
    "mode": "global",
    "log-level": "info",
    "proxies": [clash_proxy]
}

with open('/mnt/d/dev_vpn/test_mihomo_ovpn.yaml', 'w') as f:
    yaml.dump(clash_cfg, f)

print("Saved test_mihomo_ovpn.yaml")
