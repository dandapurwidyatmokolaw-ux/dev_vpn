import yaml

with open('/mnt/d/dev_vpn/test_mihomo_ovpn.yaml') as f:
    cfg = yaml.safe_load(f)

cfg['external-controller'] = '127.0.0.1:9090'
cfg['mode'] = 'global'
cfg['log-level'] = 'info'
# add proxy group
proxy_name = cfg['proxies'][0]['name']
cfg['proxy-groups'] = [
    {
        'name': 'GLOBAL',
        'type': 'select',
        'proxies': [proxy_name, 'DIRECT']
    }
]

with open('/mnt/d/dev_vpn/test_mihomo_ovpn.yaml', 'w') as f:
    yaml.dump(cfg, f)

print("Updated config with proxy-groups.")
