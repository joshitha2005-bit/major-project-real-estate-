from bs4 import BeautifulSoup
import re

path = r'C:\Users\HP\.gemini\antigravity-ide\brain\bb1a7cda-5d58-4934-abd2-91f6e1beb51d\.system_generated\steps\1570\content.md'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
# Look for pagination links or buttons
page_links = soup.find_all('a', href=re.compile(r'page|properties-for-sale'))
for a in page_links:
    href = a.get('href', '')
    if any(k in href for k in ['page', 'p=', 'pageNo', 'offset']):
        print(f"Pagination link: {href}, text: {a.get_text(strip=True)}")

# Look for locality links (nearby localities or breadcrumbs)
locality_links = [a.get('href') for a in soup.find_all('a', href=re.compile(r'properties-for-sale-in-'))]
print(f"Total locality links found: {len(locality_links)}")
for l in list(set(locality_links))[:20]:
    print("  Locality:", l)
