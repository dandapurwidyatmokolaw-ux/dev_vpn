import urllib.request
import base64
import json
import re

url = "https://raw.githubusercontent.com/freefq/free/master/v2"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10) as r:
    raw_content = r.read().decode('utf-8', errors='ignore')

# Decoding
try:
    decoded = base64.b64decode(raw_content).decode('utf-8', errors='ignore')
except:
    decoded = raw_content

lines = [line.strip() for line in decoded.splitlines() if line.strip()]
print(f"Total lines/nodes: {len(lines)}")
for l in lines[:10]:
    proto = l.split('://')[0] if '://' in l else 'unknown'
    print(f"  Proto: {proto} | Preview: {l[:50]}...")
