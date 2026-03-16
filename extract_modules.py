from bs4 import BeautifulSoup
import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://modhb.rptu.de/mhb/FB-INF/cos-506/"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req, context=ctx).read()
soup = BeautifulSoup(html, 'html.parser')

sections = soup.find_all('h2')
for sec in sections:
    if "Section" in sec.text:
        print("\n---", sec.text.strip(), "---")
        # Find the next table
        nxt = sec.find_next_sibling('table')
        if nxt:
            rows = nxt.find_all('tr')
            for r in rows:
                cols = r.find_all('td')
                if len(cols) >= 3:
                     name = cols[1].text.strip()
                     ects = cols[2].text.strip()
                     print(f"{name} | {ects}")
