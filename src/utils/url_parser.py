from urllib.parse import urlparse
from urllib.parse import unquote
from urllib.parse import parse_qs

import tldextract

from utils.config import *

# Define the mapping dictionary
# umlauts_map = {'Ä': 'AE', 'Ö': 'OE', 'Ü': 'UE', 'ß': 'ss', 'ä': 'ae', 'ö': 'oe', 'ü': 'ue'}
umlauts_map = {'ß': 'ss', 'ä': 'ae', 'ö': 'oe', 'ü': 'ue'}

# Create a translation table
umlaut_trans_table = str.maketrans(umlauts_map)

# this are commonly found steps in the paths (or giberish)
set_dashed_generic = set([
    'cgi-bin','fast-cgi', 'auth-ui', 'consent-management', 'openid-connect',
    'de-de', 'en-us', 'wba-ui', 'websso-prod', 
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
                               'surveys', 'viwweb', 'login'])


# commong extension endings in the slug
common_extension = set(['html','htm', 'pdf', 'php', 'aspx'])

# number of characters to consider in the token extraction
nb_chars = 2

# extract the search terms
def extract_search_terms(parameters):
    """
    Extracts the search terms from a parameter dictionary.

    Parameters
    ----------
    parameters : dict
        A dictionary of parameters from a URL query string.

    Returns
    -------
    str
        The extracted search terms, or an empty string if none were found.
    """

    search_terms = ' '.join(v.strip() for k, v in parameters.items() if k in URL_QUERY_PARAMS) 
    if search_terms is None or search_terms == '' or search_terms.isdigit():
        return ''
    return search_terms 


def extract_steps(path):
    """
    Extracts the steps of a path (ignoring common extensions).

    :param path: The path to extract the steps from.
    :return: The extracted steps as a list of strings.
    """

    if path == '' or path == '/':
        return []

    # ignore extensions
    if (path_split := path.rsplit('.', 1))[-1] in common_extension:
        path = path_split[0]
    
    # split the path by slashes, and remove the first which is empty
    return path.split('/')[1:]

def extract_dashed_steps(steps):
    """
    Extracts the dashed steps from a list of steps.

    The dashed steps are those containing either a dash or an underscore, and that are not in the set of fake paths
    or category related steps.

    :param steps: A list of strings representing the steps in the URL path.
    :return: A list of strings, the dashed steps.
    """

    if len(steps) == 0:
        return []

    # let's check the dashed steps, if there is at least one
    else:
        return [
            s for s in reversed(steps) 
            if ('-' in s or '_' in s) 
            and s not in set_dashed_search_or_account 
        ]

def extract_url_title(results):
    """
    Extracts a title from a URL path.

    The title is extracted in the following way:
    1. The path is split into steps.
    2. The steps with dashes or underscores are selected.
    3. The steps that are navigation related are removed.
    4. If there are more than one step, the largest one (separated by dashes) is selected.
    5. If no title is selected, the last set of the path is selected, if it is not navigation related.

    :param results: A dictionary containing the URL path as "path".
    :return: The extracted title as a string.
    """

    # extract the steps
    steps = extract_steps(results["path"])

    # extract the dashed steps
    dashed_steps = extract_dashed_steps(steps)

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


def explode_url(url: str) -> dict:
    """Returns decomposed URL as a dictionary.
    
    Args:
        url (str): The url to decompose
    
    Returns:
        dict: individual parts of the url as dictionary of the following format
        
        ```
        // tldextract (adapted)
        subdomain (str): The subdomain (without prefixed 'www') of the url
        domain (str): The domain of the url
        suffix (str): The public suffix of the url (see: https://publicsuffix.org/list/)
        registered_domain (str): The domain and suffix of the url, if both are set
        fqdn (str): The fully qualified domain name of the url

        // urllib
        scheme (str): The scheme of the url (i.e. "http", "https", ...)
        netloc (str): The network location of the url (has to be introduced by //. See: https://docs.python.org/3/library/urllib.parse.html#module-urllib.parse)
        hostname (str): The hostname of the url
        path (str): The path of the url
        params (str): The parameters of the url
        query (str): The query string of the url
        fragment (str): The fragment of the url
        
        // custom
        www (str): 'www' seperated from the subdomain (will be either empty or contain 'www')
        query_dict (dict): A dictionary of all key value pairs in the query string
        search_terms (dict): A dictionary of search_terms contained in the query string
        ```
    """

    # ------------------- URL decomposition -------------------
    #
    # foo://example.com:8042/over/there?name=ferret#nose
    # \_/ \________________/\_________/ \_________/ \__/
    # |          |             |            |        |
    # scheme    authority     path        query   fragment
    #           (netloc)

    # -------------- Domain decomposition (example) ----------------
    #
    # www.subd4.subd3.example.com
    # \_/ \_________/ \_____/ \_/
    #  |       |         |     |
    # www subdomain   domain suffix
    #                 \___________/
    #                       |
    #               registered domain
    # \___________________________/
    #               |
    #            hostname



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
    ext = urlparse(url)
    results["scheme"] = ext.scheme
    results["netloc"] = ext.netloc
    results["hostname"] = ext.hostname
    results["path"] = ext.path
    results["params"] = ext.params
    results["query"] = ext.query  
    results["fragment"] = ext.fragment  
    
    # parse the parameters of the query string, \x00 causes troubles with certain database (e.g.,mongodb), it represents a null byte
    results["query_dict"] = {k.replace('\x00', 'NULLHEX'): ' '.join(i.strip() for i in v) for k, v in parse_qs(results["query"]).items()}

    # extract the search terms
    results["search_terms"] = extract_search_terms(results["query_dict"])

    # extract the title
    results["title"] = extract_url_title(results)

    return results
