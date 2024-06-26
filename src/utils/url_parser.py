import re

from urllib.parse import urlparse
from urllib.parse import unquote
from urllib.parse import parse_qs

import tldextract



# Define the mapping dictionary
# umlauts_map = {'Ä': 'AE', 'Ö': 'OE', 'Ü': 'UE', 'ß': 'ss', 'ä': 'ae', 'ö': 'oe', 'ü': 'ue'}
umlauts_map = {'ß': 'ss', 'ä': 'ae', 'ö': 'oe', 'ü': 'ue'}

# Create a translation table
umlaut_trans_table = str.maketrans(umlauts_map)



# this are commonly found steps in the paths (or giberish)
set_dashed_generic = set([
    'cgi-bin','fast-cgi', 'auth-ui', 'consent-management', 'openid-connect',
    'de-de', 'en-us', 'wba-ui', 'websso-prod', 
    'cGJ69yA21HDKMJzAYHDxGCZmdirrbQRV-QosJ4UmQEY',
])

# this are paths that simply suggest a search or account
set_dashed_search_or_account = set([
    'meine-besucher', 'meine-huk', 'paypal-aktie', 'meine-allianz',
    'search_results', 'search-results', 'login-actions', 'login-callback',
    'your-account', 'order-history', 'deutsch-englisch'
]) | set_dashed_generic


# this are commonly found steps in the paths
set_navigation_related_steps = set([
    'tv-sender', 'live-tv', 'tv-programm', 'streamen-tv', 'tv-programm-live-stream', 'alle-kategorien',
])

# neither the fake paths nor the category related steps should be considered as titles
set_not_dashed_titles = set_dashed_search_or_account | set_navigation_related_steps

# these are ceratinly not titles
set_not_one_word_titles = set(['search', 'watch', '', 'results', 'web', 'result', 'scholar', 'url', 
                               'dsearch', 'zustimmung', 'index', 'live', 'suche', 'suchergebnisse',
                               'home', 'top', 'default', 'welcome', 'homepage', 'main', 'start',
                               'xxxxx', 'surveys', 'viwweb', 'login'])

# commong extension endings in the slug
set_extension_endings = set(['html','htm', 'pdf', 'php', 'aspx'])

# number of characters to consider in the token extraction
nb_chars = 2

# extract the search terms
def extract_search_terms(parameters):
    search_terms = ' '.join(v.strip() for k, v in parameters.items() if k in ['q', 'p', 'query', 'text', 'search_query', 'search']) # later on, i figure `psg` is an option for bing
    if search_terms is None or search_terms == '' or search_terms.isdigit():
        return ''
    return search_terms 


def extract_steps(path):
    if path == '' or path == '/':
        return []

    # ignore extensions
    if (path_split := path.rsplit('.', 1))[-1] in set_extension_endings:
        path = path_split[0]
    
    # split the path by slashes, and remove the first which is empty
    return path.split('/')[1:]

def extract_dashed_steps(steps):

    if len(steps) == 0:
        return []

    # let's check the dashed steps, if there is at least one
    else:
        return [
            s for s in reversed(steps) 
            if ('-' in s or '_' in s) 
            and s not in set_dashed_search_or_account 
        ]

def extract_url_title(steps, dashed_steps):

    title = ''

    if len(dashed_steps) > 0:
        
        # remove the navigation related steps
        not_nav_dashed_steps = [
            stripped for s in dashed_steps if s not in set_navigation_related_steps

            # this is done in the loop to make sure that the stripped is not empty
            and (stripped := s.replace('-', ' ').replace('_', ' ').strip())
        ]

        # if there are more than one step, then select the largest one (separated by dashes)
        if (len(not_nav_dashed_steps) > 0):
            title = max(not_nav_dashed_steps, key=len)


    # if not title is selected, then select the last set of the path    
    if title == '' and len(steps) > 0:
        if steps[-1] not in set_not_dashed_titles and steps[-1] not in set_not_one_word_titles:
            title = steps[-1]

    return title




def extract_url_infos(exploded_url):

    results = {}

    # extract the search terms
    results["search_terms"] = extract_search_terms(exploded_url["query_dict"])

    # signal if it is any search
    results["is_any_search"] = results["search_terms"] != ''

    # extract the steps
    steps = extract_steps(exploded_url["path"])

    # extract the dashed steps
    dashed_steps = extract_dashed_steps(steps)

    # signal if there is a dashed step
    results["has_dashed_step"] = len(dashed_steps) > 0

    # extract the url title
    results["url_title"] = extract_url_title(steps, dashed_steps)

    # signal if there is a title
    results["has_url_title"] = results["url_title"] != ''

    # extract the tokens from the title
    results["has_wordy_title"] = len(results["url_title_tokens"]) > 0

    return results


def explode_url(url: str, scheme: str = "http://") -> dict:
    """Returns decomposed URL as dictionary"""

    # ------------------- Decompose URL -------------------
    #
    # foo://example.com:8042/over/there?name=ferret#nose
    # \_/ \________________/\_________/ \_________/ \__/
    # |          |             |            |        |
    # scheme    authority     path        query   fragment
    #

    # lower case the url
    url = unquote(url).lower().translate(umlaut_trans_table)

    results = {}
    # https://github.com/john-kurkowski/tldextract
    ext = tldextract.extract(url)

    # keep the www separated as it is meaningless in 99% of the cases
    if ext.subdomain == 'www':
        results['www'] = 'www'
        results['subdomain'] = ''
    elif ext.subdomain.startswith('www.'):
        results['www'] = 'www'
        results['subdomain'] = ext.subdomain[4:]
    else:
        results['www'] = ''
        results["subdomain"] = ext.subdomain

    results["domain"] = ext.domain
    results["suffix"] = ext.suffix
    results["registered_domain"] = ext.registered_domain
    results["fqdn"] = ext.fqdn

    # https://docs.python.org/3/library/urllib.parse.html
    # Following the syntax specifications in RFC 1808, urlparse recognizes a netloc only if it is properly 
    # introduced by ‘//’. Otherwise the input is presumed to be a relative URL and thus to start with a path component.
    ext = urlparse(scheme + url)
    results["netloc"] = ext.netloc
    results["hostname"] = ext.hostname
    results["path"] = ext.path
    results["params"] = ext.params
    results["query"] = ext.query  # https://en.wikipedia.org/wiki/Query_string
    results["fragment"] = ext.fragment  # https://en.wikipedia.org/wiki/URI_fragment

    # parse the parameters of the query string, \x00 causes troubles with mongodb, it represents a null byte
    results["query_dict"] = {k.replace('\x00', 'NULLHEX'): ' '.join(i.strip() for i in v) for k, v in parse_qs(results["query"]).items()}

    return results
