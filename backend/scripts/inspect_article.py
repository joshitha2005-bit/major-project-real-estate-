import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from bs4 import BeautifulSoup
import json, re

path = r'C:\Users\HP\.gemini\antigravity-ide\brain\bb1a7cda-5d58-4934-abd2-91f6e1beb51d\.system_generated\steps\1570\content.md'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
articles = soup.find_all('article')
print(f"Total articles: {len(articles)}")

for i in range(min(3, len(articles))):
    a = articles[i]
    print(f"\n=================== ARTICLE {i} ===================")
    card_id = a.get('id')
    inner_div = a.find('div', itemscope=True)
    item_type = inner_div.get('itemtype', '') if inner_div else ''
    listing_id = inner_div.get('id', '') if inner_div else ''
    
    # Title link
    h2 = a.find('h2')
    title = h2.get_text(strip=True) if h2 else ''
    link = h2.find('a')['href'] if h2 and h2.find('a') else ''
    
    # Meta elements
    meta_dict = {}
    for m in a.find_all('meta'):
        prop = m.get('itemprop') or m.get('property') or m.get('name')
        meta_dict[prop] = m.get('content')
        
    print(f"ID: {listing_id}")
    print(f"Title: {title}")
    print(f"Link: {link}")
    print(f"Type: {item_type}")
    print(f"Metas: {json.dumps(meta_dict, indent=2)}")
    
    # Let's inspect all child divs/spans
    text_chunks = [t.strip() for t in a.stripped_strings]
    print("Strings:", text_chunks[:30])
