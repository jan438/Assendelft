# Source - https://stackoverflow.com/a/79620872
# Posted by DomTomCat, modified by community. See post 'Timeline' for change history
# Retrieved 2026-10-18, License - CC BY-SA 4.0

from urllib.request import urlopen, Request
req = Request(
        'https://a.tile.openstreetmap.org/14/8381/5845.png',  
        headers={
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0'
        }
    )
data = urlopen(req).read()

with open("PDF/test.png", 'wb') as out:
    out.write(data)

key = input("Wait")
