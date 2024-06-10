from selectolax.parser import HTMLParser
from trafilatura import extract

from utils.local import *

SELECTOLAX_DIR = 'data/selectolax'
TRAFILATURA_DIR = 'data/trafilatura'

def extractText(id: str):
    """Extracts the actual text from an HTML document associated with a task (selectolax)"""

    # First check if there already is a parsed version in the selectolax directory
    try:
        with open(f'{SELECTOLAX_DIR}/{id}.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        # get page content
        html_document = getPageContent(id)

        if html_document is None:
            return None
        
        tree = HTMLParser(html_document)

        if tree.body is None:
            return None

        for tag in tree.css('script'):
            tag.decompose()
        for tag in tree.css('style'):
            tag.decompose()

        text = tree.body.text(separator='\n')

        # Save the parsed version
        with open(f'{SELECTOLAX_DIR}/{id}.txt', 'w') as f:
            f.write(text)
        
        return text

def extractTextTrafilatura(id: str):
    """Extracts the actual text from an HTML document associated with a task (trafilatura)"""

    # First check if there already is a parsed version in the trafilatura directory
    try:
        with open(f'{TRAFILATURA_DIR}/{id}.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        html_document = getPageContent(id)
        
        if html_document is None:
            return None
        
        text = extract(html_document)

        if text is None:
            return None

        # Save the parsed version
        with open(f'{TRAFILATURA_DIR}/{id}.txt', 'w') as f:
            f.write(text)
        
        return text