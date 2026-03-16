import urllib.request
from bs4 import BeautifulSoup
import ssl
import sys

def fetch_url(url):
    print(f"Fetching {url}...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        html = urllib.request.urlopen(req, context=ctx).read()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract main text content
        text = soup.get_text(separator='\n', strip=True)
        print("Success! First 2000 characters:")
        print("-" * 50)
        print(text[:2000])
        print("-" * 50)
        
        # Try to find tables or lists that might contain modules
        print("Looking for tables...")
        tables = soup.find_all('table')
        for i, table in enumerate(tables):
            print(f"Table {i+1}:")
            print(table.get_text(separator=' | ', strip=True)[:500])
            
    except Exception as e:
        print(f"Error fetching: {e}")

if __name__ == "__main__":
    urls = [
        "https://www.cs.rptu.de/studium/studiengaenge/bm-inf/sp.ba/",
        "https://rptu.de/studium/studiengaenge/bachelorstudiengaenge/informatik-bachelor",
        "https://cs.rptu.de/studium/studiengaenge/bachelor/informatik"
    ]
    for u in urls:
        fetch_url(u)
        print("\n" + "="*50 + "\n")
