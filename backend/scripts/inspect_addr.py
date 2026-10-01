from bs4 import BeautifulSoup

path = r'C:\Users\HP\.gemini\antigravity-ide\brain\bb1a7cda-5d58-4934-abd2-91f6e1beb51d\.system_generated\steps\1570\content.md'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
articles = soup.find_all('article')
a4 = articles[4]
# Check header section of article 4
section = a4.find('section')
if section:
    for div in section.find_all(['div', 'span', 'h2']):
        txt = div.get_text(strip=True)
        if len(txt) > 5 and len(txt) < 150:
            print(f"[{div.name} class={div.get('class')}]: {txt}")
