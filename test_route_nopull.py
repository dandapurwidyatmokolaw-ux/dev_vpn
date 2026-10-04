import json
import base64
import re
import os

with open('/mnt/d/dev_vpn/vpn.json') as f:
    data = json.load(f)

# Buat config openvpn standar untuk server online
online = [s for s in data['servers'] if s.get('status') == 'online']

for idx, s in enumerate(online[:3]):
    cfg = base64.b64decode(s['config_base64']).decode('utf-8', errors='ignore')
    
    # Supaya tidak mengubah default gateway laptop, tambahkan directive:
    # route-nopull (artinya jangan override default route!)
    # route-noexec
    custom_cfg = cfg + "\nroute-nopull\n"
    
    fname = f"/mnt/d/dev_vpn/server_{idx+1}.ovpn"
    with open(fname, 'w') as f:
        f.write(custom_cfg)
    print(f"Server {idx+1}: {s['country']} ({s['ip']}:{s['port']}) saved to {fname}")
