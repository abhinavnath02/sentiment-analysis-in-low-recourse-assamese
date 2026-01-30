import requests
from bs4 import BeautifulSoup
import logging

urls = [
    "https://www.asomiyapratidin.in/homepage/ongc-rig-fire-news-sivsagar-11056472",
    "https://niyomiyabarta.com/assam/tragic-mother-and-son-die-in-fire-in-kanikuchi-rangia/"
]

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Research Pipeline; Assamese Sentiment Project) requests/2.31'
})

for url in urls:
    print(f"--- Analyzing {url} ---")
    try:
        resp = session.get(url, timeout=10)
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Find the paragraph with the most text to locate the main content container
        paragraphs = soup.find_all('p')
        if not paragraphs:
            print("No <p> tags found.")
            continue
            
        longest_p = max(paragraphs, key=lambda p: len(p.get_text()))
        parent = longest_p.parent
        
        print(f"Longest paragraph text snippet: {longest_p.get_text()[:50]}...")
        print(f"Parent Tag: <{parent.name}>")
        print(f"Parent Attributes: {parent.attrs}")
        
        # Also check for h1
        title = soup.find('h1')
        print(f"H1 found: {title.get_text() if title else 'None'}")
        
    except Exception as e:
        print(f"Error: {e}")
    print("\n")
