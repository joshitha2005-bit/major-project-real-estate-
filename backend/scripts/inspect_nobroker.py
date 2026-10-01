import os, json
from bs4 import BeautifulSoup

path = r'C:\Users\HP\.gemini\antigravity-ide\brain\bb1a7cda-5d58-4934-abd2-91f6e1beb51d\.system_generated\steps\1570\content.md'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
articles = soup.find_all('article')
print(f"Total articles found: {len(articles)}")

scripts = soup.find_all('script', type='application/ld+json')
print(f"Total ld+json scripts: {len(scripts)}")
for idx, s in enumerate(scripts):
    try:
        data = json.loads(s.string)
        print(f"Script {idx}: keys={list(data.keys()) if isinstance(data, dict) else type(data)}")
        if isinstance(data, dict) and '@type' in data:
            print(f"  @type={data['@type']}")
            if data['@type'] == 'ItemList':
                items = data.get('itemListElement', [])
                print(f"  ItemList length: {len(items)}")
                if items:
                    print("  Sample item 0:", json.dumps(items[0], indent=2)[:500])
    except Exception as e:
        print(f"Script {idx} error: {e}")

if articles:
    a0 = articles[0]
    print("\n--- SAMPLE ARTICLE 0 ---")
    print(a0.prettify()[:1500])
