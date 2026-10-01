import json
from bs4 import BeautifulSoup

path = r'C:\Users\HP\.gemini\antigravity-ide\brain\bb1a7cda-5d58-4934-abd2-91f6e1beb51d\.system_generated\steps\1570\content.md'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
scripts = soup.find_all('script', type='application/ld+json')
for s in scripts:
    try:
        d = json.loads(s.string)
        if d.get('@type') == ['FAQPage'] or d.get('@type') == 'FAQPage':
            print("FAQ Data:")
            print(json.dumps(d, indent=2)[:2000])
    except:
        pass

# Check any tables or overview sections
for t in soup.find_all('table'):
    print("Table found:", t.get_text(separator=' | ', strip=True)[:500])
