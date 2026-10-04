import json
import base64

ovpn_file = '/mnt/d/dev_vpn/current.ovpn'

singbox_config = {
    "log": {
        "level": "info",
        "timestamp": True
    },
    "inbounds": [
        {
            "type": "mixed",
            "tag": "mixed-in",
            "listen": "0.0.0.0",
            "listen_port": 10808
        }
    ],
    "outbounds": [
        {
            "type": "openvpn",
            "tag": "ovpn-out",
            "file_path": ovpn_file
        }
    ]
}

config_json_path = '/mnt/d/dev_vpn/test_singbox.json'
with open(config_json_path, 'w') as f:
    json.dump(singbox_config, f, indent=2)

print("Updated config saved.")
