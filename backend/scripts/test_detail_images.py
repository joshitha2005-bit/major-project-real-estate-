import urllib.request, ssl, re, json
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}
url = 'https://www.nobroker.in/property/buy/2-bhk-apartment-for-sale-in-jakkasandra-bangalore/8aa98dc59ebfe60c019ec13f371e2e3a/detail'
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"HTTP {resp.getcode()}, length {len(html)} bytes")
        pattern = r'https://images\.nobroker\.in/images/8aa98dc59ebfe60c019ec13f371e2e3a/[^\s\"\'\\]+'
        imgs = set(re.findall(pattern, html))
        print(f"Found property-specific images: {len(imgs)}")
        for img in list(imgs)[:6]:
            print("  ", img)
except Exception as e:
    print(f"Error: {e}")
