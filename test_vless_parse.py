import urllib.parse
import re

def parse_vless(url):
    tag = ""
    if "#" in url:
        url, tag = url.split("#", 1)
        tag = urllib.parse.unquote(tag)
    
    url = url[8:] # strip vless://
    userinfo, hostinfo = url.split("@", 1)
    uuid = userinfo
    
    if "?" in hostinfo:
        server_port, query_str = hostinfo.split("?", 1)
        params = urllib.parse.parse_qs(query_str)
    else:
        server_port = hostinfo
        params = {}
        
    server, port = server_port.split(":", 1)
    
    proxy = {
        "name": tag or f"vless-{server}",
        "type": "vless",
        "server": server,
        "port": int(port),
        "uuid": uuid,
        "cipher": "auto",
        "tls": params.get('security', [''])[0].lower() in ['tls', 'reality'],
        "network": params.get('type', ['tcp'])[0]
    }
    
    if params.get('sni'):
        proxy['servername'] = params['sni'][0]
    if params.get('flow'):
        proxy['flow'] = params['flow'][0]
    if params.get('security', [''])[0].lower() == 'reality':
        proxy['reality-opts'] = {
            'public-key': params.get('pbk', [''])[0],
            'short-id': params.get('sid', [''])[0]
        }
    if proxy['network'] == 'ws':
        proxy['ws-opts'] = {
            'path': params.get('path', ['/'])[0],
            'headers': {'Host': params.get('host', [server])[0]}
        }
    return proxy

# Test link
link = "vless://e3e9805a-6c8b-4edd-8ee8-621df79806eb@162.35.242.252:443?encryption=none&security=reality&sni=nl.aksay.pro&fp=chrome&pbk=ClG6fvriBTK8donGsTlKusJ0dwRCgVDDTAGzAtZzJDY&sid=82c2b7d5e70ff000&type=tcp&headerType=none#TestReality"
print(parse_vless(link))
