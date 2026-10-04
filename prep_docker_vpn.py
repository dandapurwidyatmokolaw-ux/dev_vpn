import json
import base64
import os
import subprocess
import time

with open('/mnt/d/dev_vpn/vpn.json') as f:
    data = json.load(f)

# Ambil server online pertama
server = data['servers'][0]
cfg = base64.b64decode(server['config_base64']).decode('utf-8', errors='ignore')

# Tambahkan auth-user-pass dummy jika diperlukan dan verb
cfg += "\nauth-user-pass /etc/openvpn/auth.txt\n"

os.makedirs('/mnt/d/dev_vpn/docker_vpn', exist_ok=True)
with open('/mnt/d/dev_vpn/docker_vpn/vpn.ovpn', 'w') as f:
    f.write(cfg)

with open('/mnt/d/dev_vpn/docker_vpn/auth.txt', 'w') as f:
    f.write("vpn\nvpn\n")

print("Config written for Docker VPN test.")
