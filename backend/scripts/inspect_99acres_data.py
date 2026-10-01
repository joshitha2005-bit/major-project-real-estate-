import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from bs4 import BeautifulSoup
import json

path = r'C:\Users\HP\.gemini\antigravity-ide\brain\bb1a7cda-5d58-4934-abd2-91f6e1beb51d\.system_generated\steps\1713\content.md'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
scripts = soup.find_all('script')
s8 = scripts[8].string
idx = s8.find('window.__initialData__=') + len('window.__initialData__=')
raw_str = s8[idx:].strip()
decoder = json.JSONDecoder()
obj, _ = decoder.raw_decode(raw_str)

rlp = obj.get('rlp', {})
locs = rlp.get('localityListData', {}).get('tuple', [])
print(f"Total localities extracted: {len(locs)}")
for i, l in enumerate(locs[:10]):
    print(f"{i+1}. {l.get('localityName')}: Rate={l.get('pricePerSqFt')}, YoY={l.get('appreciation')}, Yield={l.get('rentalYield')}, Range={l.get('budgetRange')}, Tag={l.get('tags')}")
