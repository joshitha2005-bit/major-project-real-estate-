import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from bs4 import BeautifulSoup
import json, re

path = r'C:\Users\HP\.gemini\antigravity-ide\brain\bb1a7cda-5d58-4934-abd2-91f6e1beb51d\.system_generated\steps\1713\content.md'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
# Look for script tags with initial state or window.__INITIAL_STATE__
scripts = soup.find_all('script')
print(f"Scripts count: {len(scripts)}")
for idx, s in enumerate(scripts):
    txt = s.string or ""
    if any(k in txt for k in ['priceTrend', 'localityList', 'tableData', 'rates', 'subLocality', 'INIT_STATE']):
        print(f"Script {idx} matched keyword! Length: {len(txt)}")
        # Check snippet
        print("  Snippet:", txt[:300].replace('\n', ' '))

# Check tables
tables = soup.find_all('table')
print(f"Tables count: {len(tables)}")
for i, t in enumerate(tables):
    rows = t.find_all('tr')
    print(f"Table {i} rows: {len(rows)}")
    for r in rows[:5]:
        print("   Row:", [c.get_text(strip=True) for c in r.find_all(['th', 'td'])])
