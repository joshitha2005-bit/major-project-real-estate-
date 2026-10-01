import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    ("Housing Koramangala", "https://housing.com/in/buy/bengaluru/koramangala-gid/"),
    ("Magicbricks Koramangala", "https://www.magicbricks.com/property-for-sale-in-koramangala-bangalore-pppfs"),
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

for name, url in urls:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            print(f"{name}: HTTP {resp.getcode()}, length {len(resp.read())}")
    except urllib.error.HTTPError as e:
        print(f"{name}: HTTP Error {e.code} ({e.reason})")
    except Exception as e:
        print(f"{name}: Error {e}")
