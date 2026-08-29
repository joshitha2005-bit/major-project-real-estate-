import urllib.request
import urllib.parse
import re
import ssl

def search_bing_thumbnails(query: str, count: int = 5):
    url = f"https://www.bing.com/images/search?q={urllib.parse.quote(query)}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    ssl_ctx = ssl._create_unverified_context()
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10, context=ssl_ctx) as response:
            body = response.read().decode('utf-8')
            
            # Find URLs containing bing.net/th
            # e.g., https://tse4.mm.bing.net/th/id/OIP.enrNoK8g-LERypnwV627ZgHaJ4?w=194&h=259
            matches = re.findall(r'src="(https?://[^"]*bing\.net/th/[^"]+)"', body)
            
            # Replace amp; with & in URLs
            urls = []
            for m in matches:
                clean_url = m.replace('&amp;', '&')
                if clean_url not in urls:
                    urls.append(clean_url)
                    if len(urls) >= count:
                        break
            return urls
    except Exception as e:
        print(f"Error: {e}")
        return []

test_query = "Brigade Orchid Padmanabhanagar Bengaluru exterior"
urls = search_bing_thumbnails(test_query)
print(f"Found {len(urls)} thumbnails:")
for u in urls:
    print(u)
