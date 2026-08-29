import urllib.request
import json
import ssl

ssl_ctx = ssl._create_unverified_context()

def test_endpoint(url):
    print(f"Testing URL: {url}")
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10, context=ssl_ctx) as response:
            status = response.getcode()
            body = response.read().decode('utf-8')
            print(f"Status Code: {status}")
            data = json.loads(body)
            # Print the first item info
            if "items" in data:
                items = data["items"]
                print(f"Total items returned: {len(items)}")
                if items:
                    print(f"First property ID: {items[0].get('id')}")
                    print(f"First property Title: {items[0].get('title')}")
                    print(f"First property Images: {items[0].get('images')}")
            else:
                print(f"Property ID: {data.get('id')}")
                print(f"Property Title: {data.get('title')}")
                print(f"Property Images: {data.get('images')}")
    except Exception as e:
        print(f"Error testing URL {url}: {e}")

test_endpoint("http://localhost:8000/api/v1/properties/?page=1&page_size=3")
test_endpoint("http://localhost:8000/api/v1/properties/11900")
