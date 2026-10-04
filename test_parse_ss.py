import json
import base64
import urllib.parse

# Contoh parse ss link
# ss://method:password@host:port#tag
# atau ss://base64(method:password)@host:port#tag
# atau ss://base64(method:password@host:port)#tag

def parse_ss(url):
    tag = ""
    if "#" in url:
        url, tag = url.split("#", 1)
        tag = urllib.parse.unquote(tag)
    url = url[5:] # strip ss://
    if "@" in url:
        userinfo, serverinfo = url.split("@", 1)
        if ":" in userinfo:
            method, password = userinfo.split(":", 1)
        else:
            decoded = base64.b64decode(userinfo + "==").decode('utf-8')
            method, password = decoded.split(":", 1)
    else:
        decoded = base64.b64decode(url + "==").decode('utf-8')
        userinfo, serverinfo = decoded.split("@", 1)
        method, password = userinfo.split(":", 1)
        
    serverinfo = serverinfo.split("?")[0]
    host, port = serverinfo.split(":", 1)
    return {
        "type": "shadowsocks",
        "tag": tag or f"ss-{host}",
        "server": host,
        "server_port": int(port),
        "method": method,
        "password": password
    }

sample_ss = "ss://Y2hhY2hhMjAtaWV0Zi1wb2x5MTMwNTpJWGEzeWx6U19qQk9Bc1F5MDcxdElR@94.249.187.46:1080#Server 2 🇩🇪"
print("Parsed SS:", parse_ss(sample_ss))
