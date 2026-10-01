import re
from bs4 import BeautifulSoup

path = r'C:\Users\HP\.gemini\antigravity-ide\brain\bb1a7cda-5d58-4934-abd2-91f6e1beb51d\.system_generated\steps\1570\content.md'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# Look for price trends, avg price, or locality stats in the HTML
matches = re.findall(r'([^.\n]*?(?:price trend|average price|rates in|sq\.ft|price/sqft)[^.\n]*)', html, re.I)
print(f"Matches count: {len(matches)}")
for m in set(matches[:20]):
    print("Match:", m.strip())
