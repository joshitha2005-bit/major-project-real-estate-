import urllib.request, ssl
from bs4 import BeautifulSoup

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

new_locs = [
    ("Kanakapura Road", "https://www.nobroker.in/properties-for-sale-in-kanakapura-road-bangalore"),
    ("Bannerghatta Road", "https://www.nobroker.in/properties-for-sale-in-bannerghatta-road-bangalore"),
    ("Sarjapur", "https://www.nobroker.in/properties-for-sale-in-sarjapur-bangalore"),
    ("Kudlu Gate", "https://www.nobroker.in/properties-for-sale-in-kudlu-gate-bangalore"),
    ("Kasavanahalli", "https://www.nobroker.in/properties-for-sale-in-kasavanahalli-bangalore"),
    ("Panathur", "https://www.nobroker.in/properties-for-sale-in-panathur-bangalore"),
    ("Horamavu", "https://www.nobroker.in/properties-for-sale-in-horamavu-bangalore"),
    ("Hennur Road", "https://www.nobroker.in/properties-for-sale-in-hennur-road-bangalore"),
    ("Basavanagudi", "https://www.nobroker.in/properties-for-sale-in-basavanagudi-bangalore"),
    ("Vijayanagar", "https://www.nobroker.in/properties-for-sale-in-vijayanagar-bangalore"),
]

for name, url in new_locs:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            soup = BeautifulSoup(resp.read(), 'html.parser')
            articles = soup.find_all('article')
            print(f"{name}: HTTP {resp.getcode()}, articles: {len(articles)}")
    except Exception as e:
        print(f"{name}: {e}")
