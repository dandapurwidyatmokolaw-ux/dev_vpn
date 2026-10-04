import json

outbound = {
    "type": "shadowsocks",
    "tag": "ss-out",
    "server": "94.249.187.46",
    "server_port": 1080,
    "method": "chacha20-ietf-poly1305",
    "password": "IXa3ylzS_jBOAsQy071tIQ"
}

singbox_cfg = {
    "log": {"level": "info"},
    "inbounds": [
        {
            "type": "mixed",
            "tag": "mixed-in",
            "listen": "127.0.0.1",
            "listen_port": 10808
        }
    ],
    "outbounds": [outbound]
}

with open('/mnt/d/dev_vpn/test_ss_cfg.json', 'w') as f:
    json.dump(singbox_cfg, f, indent=2)

print("Saved test_ss_cfg.json")
