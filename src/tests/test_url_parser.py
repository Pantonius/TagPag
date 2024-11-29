from utils.config import *
from utils.url_parser import *

load_environment('tests_data/.env-test', force=True)
config = Config()

def test_extract_search_terms():
    # 1. should only extract q,p,query,text,search_query,search,psg
    parameters = {
        'q': 'github',
        'lang': 'python',
        'p' : '1',
        'query': 'git',
        'text': 'copilot',
        'search_query': 'github',
        'search': 'git',
        'psg': '1',
        'page': '1',
        'size': '10'
    }
    expected_terms = 'github 1 git copilot github git 1'
    actual_terms = extract_search_terms(parameters)

    assert actual_terms == expected_terms

    # 2. should return empty string if no search terms are found
    parameters = {
        'lang': 'python',
        'page': '1',
        'size': '10'
    }
    expected_terms = ''
    actual_terms = extract_search_terms(parameters)

    assert actual_terms == expected_terms

    # 3. shoudl return empty string if search terms are empty
    parameters = {
        'q': '',
        'lang': 'python',
        'page': '1',
        'size': '10'
    }
    expected_terms = ''
    actual_terms = extract_search_terms(parameters)

    assert actual_terms == expected_terms

    # 4. should return empty string if search terms are only whitespace
    parameters = {
        'q': ' ',
        'lang': 'python',
        'page': '1',
        'size': '10'
    }

    expected_terms = ''
    actual_terms = extract_search_terms(parameters)

    assert actual_terms == expected_terms

    # 5. should return empty string if no parameters are passed
    parameters = {}
    expected_terms = ''
    actual_terms = extract_search_terms(parameters)

    assert actual_terms == expected_terms

def test_extract_steps():
    test_cases = [
        ('/git/tagpag/src/utils/url_parser.py', ['git', 'tagpag', 'src', 'utils', 'url_parser.py']), # 1. should return a list of steps from a path
        ('', []), # 2. should return empty list if path is empty
        (None, []) # 3. should return empty list if path is None
    ]

    for test_case in test_cases:
        assert extract_steps(test_case[0]) == test_case[1]

def test_extract_dashed_steps():
    test_cases = [
        (['git', 'tag-pag', 'src', 'utils', 'url_parser.py'], ['tag-pag', 'url_parser.py']), # 1. should return a list of dashed steps
        ([], []), # 2. should return an empty list if steps is empty
        (None, []) # 3. should return an empty list if steps is None
    ]

    for test_case in test_cases:
        assert extract_dashed_steps(test_case[0]) == test_case[1]

def test_extract_url_title():
    test_cases = {
        '': '', # empty title
        '/page': 'page', # simple page
        '/pageWithSlash/': 'pageWithSlash', # page with trailing slash
        '/some/other/longer_page': 'longer_page' # longer path to page with dash
    }

    for test_case in test_cases:
        result = {
            'path': test_case,
        }

        extracted_title = extract_url_title(result)

        assert extracted_title == test_cases[test_case]

def test_explode_url():
    url = 'https://github.com/microsoft/GitHubCopilot'
    expected_exploded_url = {
        'www': '',
        'subdomain': '',
        'domain': 'github',
        'suffix': 'com',
        'registered_domain': 'github.com',
        'fqdn': 'github.com',
        'scheme': 'https',
        'netloc': 'github.com',
        'hostname': 'github.com',
        'path': '/microsoft/githubcopilot',
        'params': '',
        'query': '',
        'fragment': '',
        'query_dict': {},
        'search_terms': '',
        'title': 'githubcopilot'
    }
    actual_exploded_url = explode_url(url)

    assert actual_exploded_url == expected_exploded_url

def test_explode_url_with_www():
    url = 'https://www.github.com/microsoft/GitHubCopilot'
    expected_exploded_url = {
        'www': 'www',
        'subdomain': '',
        'domain': 'github',
        'suffix': 'com',
        'registered_domain': 'github.com',
        'fqdn': 'www.github.com',
        'scheme': 'https',
        'netloc': 'www.github.com',
        'hostname': 'www.github.com',
        'path': '/microsoft/githubcopilot',
        'params': '',
        'query': '',
        'fragment': '',
        'query_dict': {},
        'search_terms': '',
        'title': 'githubcopilot'
    }
    actual_exploded_url = explode_url(url)

    assert actual_exploded_url == expected_exploded_url

def test_explode_url_with_www_in_subdomain():
    url = 'https://www.subdomain.github.com/microsoft/GitHubCopilot'
    expected_exploded_url = {
        'www': 'www',
        'subdomain': 'subdomain',
        'domain': 'github',
        'suffix': 'com',
        'registered_domain': 'github.com',
        'fqdn': 'www.subdomain.github.com',
        'scheme': 'https',
        'netloc': 'www.subdomain.github.com',
        'hostname': 'www.subdomain.github.com',
        'path': '/microsoft/githubcopilot',
        'params': '',
        'query': '',
        'fragment': '',
        'query_dict': {},
        'search_terms': '',
        'title': 'githubcopilot'
    }
    actual_exploded_url = explode_url(url)

    assert actual_exploded_url == expected_exploded_url