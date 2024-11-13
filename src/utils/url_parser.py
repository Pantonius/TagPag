from urllib.parse import urlparse
from urllib.parse import unquote
from urllib.parse import parse_qs

import tldextract

from utils.config import *

# Get the special character map
env = load_environment_variables()

# Create a translation table
special_map_table = str.maketrans(env.SPECIAL_CHARACTER_MAP)


# extract the search terms
def extract_search_terms(parameters) -> str:
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

    search_terms = ' '.join(v.strip() for k, v in parameters.items() if k in env.URL_QUERY_PARAMS) 
    if search_terms is None or search_terms == '' or search_terms.isdigit():
        return ''
    return search_terms 


def extract_steps(path) -> list:
    """
    Extracts the steps of a path (ignoring common extensions).

    :param path: The path to extract the steps from.
    :return: The extracted steps as a list of strings.
    """

    if path == None or path == '' or path == '/':
        return []
    
    # ignore extensions
    if (path_split := path.rsplit('.', 1))[-1] in env.COMMON_EXTENSIONS:
        path = path_split[0]
    
    # split the path by slashes, and remove the first which is empty
    steps = path.split('/')[1:]
    if steps[-1] == '':
        steps.pop()

    return steps

def extract_dashed_steps(steps) -> list:
    """
    Extracts the dashed steps from a list of steps.

    The dashed steps are those containing either a dash or an underscore, and that are not in the set of fake paths
    or category related steps.

    :param steps: A list of strings representing the steps in the URL path.
    :return: A list of strings, the dashed steps.
    """

    if steps is None or len(steps) == 0:
        return []

    # let's check the dashed steps, if there is at least one
    else:
        return [
            s for s in reversed(steps)
            if ('-' in s or '_' in s) 
            and s not in env.NOT_SEO_TITLES 
        ]

def extract_url_title(results: dict) -> str:
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
    print(steps)

    # extract the dashed steps
    dashed_steps = extract_dashed_steps(steps)

    title = ''

    if len(dashed_steps) > 0:
        
        # remove the navigation related steps
        not_nav_dashed_steps = [
            s for s in dashed_steps if s not in env.NOT_SEO_TITLES

            # this is done in the loop to make sure that the stripped is not empty
            and (s.replace('-', ' ').replace('_', ' ').strip())
        ]

        # if there are more than one step, then select the largest one (separated by dashes)
        if (len(not_nav_dashed_steps) > 0):
            title = max(not_nav_dashed_steps, key=len)

    # if not title is selected, then select the last set of the path    
    if title == '' and len(steps) > 0:
        if steps[-1] not in env.NOT_SEO_TITLES and steps[-1] != '':
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
        title (str): The title extracted from the path
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
    url = unquote(url).lower().translate(special_map_table)

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
