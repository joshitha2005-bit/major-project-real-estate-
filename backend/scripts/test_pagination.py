import urllib.request, ssl
from bs4 import BeautifulSoup

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

url_p2 = "https://www.nobroker.in/properties-for-sale-in-koramangala-bangalore?pageNo=2"
req = urllib.request.Request(url_p2, headers=headers)
try:
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        soup = BeautifulSoup(resp.read(), 'html.parser')
        articles = soup.find_all('article')
        print(f"Page 2 articles: {len(articles)}")
        if articles:
            print("Page 2 article 0 title:", articles[0].find('h2').get_text(strip=True) if articles[0].find('h2') else 'none')
except Exception as e:
    print(f"Page 2 error: {e}")
