import urllib.request, ssl
from bs4 import BeautifulSoup

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

urls = [
    ("Rates Bangalore", "https://www.nobroker.in/property/buy/rates/bangalore"),
    ("Locality IQ Whitefield", "https://www.nobroker.in/locality-iq/Whitefield"),
]

for name, url in urls:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            content = resp.read()
            soup = BeautifulSoup(content, 'html.parser')
            print(f"{name}: HTTP {resp.getcode()}, length {len(content)}, title: {soup.title.string if soup.title else 'none'}")
    except urllib.error.HTTPError as e:
        print(f"{name}: HTTP {e.code}")
    except Exception as e:
        print(f"{name}: error {e}")
