import urllib.request
import time

proxies_to_test = [
    '208.102.51.6:58208',
    '69.61.200.104:36181',
    '66.42.224.229:41679',
    '174.64.199.82:4145',
    '192.111.130.5:17002'
]

for p in proxies_to_test:
    proxy_url = f"socks5h://{p}"
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({'http': proxy_url, 'https': proxy_url}))
    try:
        t0 = time.time()
        with opener.open('https://api.ipify.org', timeout=5) as r:
            ip = r.read().decode('utf-8').strip()
            print(f"SUCCESS: Proxy {p} -> IP Keluar: {ip} (Waktu: {round((time.time()-t0)*1000)} ms)")
    except Exception as e:
        print(f"FAIL {p}: {e}")
