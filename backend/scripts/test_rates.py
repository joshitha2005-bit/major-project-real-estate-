import urllib.request, ssl
from bs4 import BeautifulSoup

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

rate_urls = [
    ("Bangalore Rates", "https://www.nobroker.in/property-rates-in-bangalore"),
    ("Koramangala Rates", "https://www.nobroker.in/property-rates-in-koramangala-bangalore"),
]

for name, url in rate_urls:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            content = resp.read()
            soup = BeautifulSoup(content, 'html.parser')
            print(f"{name}: HTTP {resp.getcode()}, length {len(content)}, title: {soup.title.string if soup.title else 'none'}")
            # check tables or price info
            tables = soup.find_all('table')
            print(f"  Tables found: {len(tables)}")
    except Exception as e:
        print(f"{name}: error {e}")
