from bs4 import BeautifulSoup
from selectolax.parser import HTMLParser

def extractText(html_document: str):
    """Extracts the actual text from an HTML document"""

    # soup = BeautifulSoup(html_document, features="html.parser")

    # # Kill all script and style elements
    # for script in soup(["script", "style"]):
    #     script.extract()  # Rip it out

    # # Get text
    # text = soup.get_text()
    # # Break into lines and remove leading and trailing space on each
    # # lines = (line.strip() for line in text.splitlines())
    # # Break multi-headlines into a line each
    # # chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # # Drop blank lines
    # # text = "\n".join(chunk for chunk in chunks if chunk)

    tree = HTMLParser(html_document)

    if tree.body is None:
        return None

    for tag in tree.css('script'):
        tag.decompose()
    for tag in tree.css('style'):
        tag.decompose()

    text = tree.body.text(separator='\n')

    return text
