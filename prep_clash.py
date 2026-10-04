import yaml
import json

with open('/mnt/d/dev_vpn/test_clash.yaml', 'r', encoding='utf-8') as f:
    cfg = yaml.safe_load(f)

proxies = cfg.get('proxies', [])
print('Total proxies in test_clash.yaml:', len(proxies))

# Pick first 5 valid proxies
selected = proxies[:10]

simple_cfg = {
    'port': 10808,
    'socks-port': 10809,
    'allow-lan': True,
    'mode': 'global',
    'log-level': 'warning',
    'external-controller': '127.0.0.1:9090',
    'proxies': selected
}

with open('/mnt/d/dev_vpn/active_clash.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(simple_cfg, f, allow_unicode=True)

print("Saved active_clash.yaml with", len(selected), "nodes.")
