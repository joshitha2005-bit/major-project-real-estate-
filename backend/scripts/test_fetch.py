import urllib.request
import ssl
import time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    ("Koramangala", "https://www.nobroker.in/properties-for-sale-in-koramangala-bangalore"),
    ("Indiranagar", "https://www.nobroker.in/properties-for-sale-in-indiranagar-bangalore"),
    ("Whitefield", "https://www.nobroker.in/properties-for-sale-in-whitefield-bangalore"),
    ("HSR Layout", "https://www.nobroker.in/properties-for-sale-in-hsr-layout-bangalore"),
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

for name, url in urls:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            code = resp.getcode()
            content = resp.read()
            print(f"{name}: HTTP {code}, length {len(content)} bytes")
    except Exception as e:
        print(f"{name}: Failed with {e}")
    time.sleep(1)
