import json
import base64
import os

with open('/mnt/d/dev_vpn/vpn.json') as f:
    data = json.load(f)

# Server 2: Viet Nam (42.118.129.186:1513)
s = data['servers'][1]
print("Target server:", s['country'], s['ip'], s['port'])
cfg = base64.b64decode(s['config_base64']).decode('utf-8', errors='ignore')

with open('/mnt/d/dev_vpn/docker_vpn/vietnam.ovpn', 'w') as f:
    f.write(cfg)

print("Saved /mnt/d/dev_vpn/docker_vpn/vietnam.ovpn")
