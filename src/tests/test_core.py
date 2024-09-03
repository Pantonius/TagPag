from utils.core import highlight_url

def test_highlight_url():
    # Test cases for highlight_url
    
    # 1. Without truncation: Should just wrap the FQDN and path with asterisks
    assert highlight_url('https://some.website.com') == 'https://<strong>some.website.com</strong>'  # scheme://FQDN
    assert highlight_url('https://some.website.com/long/path/to_some_file.html') == 'https://<strong>some.website.com</strong>/long/path/<strong>to_some_file</strong>.html'  # scheme://FQDN/path
    assert highlight_url('https://some.website.com/search?q=python') == 'https://<strong>some.website.com</strong>/<strong>search</strong>?q=<strong>python</strong>'  # scheme://FQDN/path?query=param where the query string contains a search term
    assert highlight_url('https://some.website.com/search?q=python&lang=en') == 'https://<strong>some.website.com</strong>/<strong>search</strong>?q=<strong>python</strong>&lang=en'  # scheme://FQDN/path?query=param&query=param where the query string contains one search term
    assert highlight_url('https://some.website.com/search?q=python#section') == 'https://<strong>some.website.com</strong>/<strong>search</strong>?q=<strong>python</strong>#section'  # scheme://FQDN/path#fragment

    # 2. With truncation: Should truncate the URL and wrap the FQDN and path with asterisks even if they are truncated
    # TODO: Implement this test case
    