import pytest
from utils.html_truncator import HTMLTruncator

def test_no_truncation_needed():
    """
    Test case for when no truncation is needed.
    
    The HTML is short enough that no truncation is necessary, so the original
    HTML should be returned.
    """
    
    html = "<p>Hello, world!</p>"
    truncator = HTMLTruncator(limit=50)
    truncator.feed(html)
    assert truncator.get_truncated_html() == html

def test_truncation_in_middle_of_text():
    """
    Test case for when truncation is needed in the middle of a text node.

    The HTML contains a text node that exceeds the truncation limit, so the
    text should be truncated at the limit and an ellipsis added to indicate
    that the text has been truncated.
    """
    
    html = '<p class="ignore">Hello, world!</p>'
    truncator = HTMLTruncator(limit=5)
    truncator.feed(html)
    assert truncator.get_truncated_html() == '<p class="ignore">Hello...</p>'

def test_truncation_at_end_of_tag():
    """
    Test case for when truncation is needed at the end of a tag.

    The HTML is longer than the truncation limit, but the last node is a tag
    rather than a text node. The tag should be truncated and a closing tag
    should be added to the end of the HTML string.
    """

    html = "<p>Hello, world!</p>"
    truncator = HTMLTruncator(limit=7)
    truncator.feed(html)
    assert truncator.get_truncated_html() == "<p>Hello, ...</p>"

def test_truncation_with_nested_tags():
    """
    Test case for when truncation is needed with nested tags.

    The HTML contains nested tags, and the truncation limit falls within one of
    the nested tags. The text should be truncated at the limit, and the nested
    tag should be properly closed.
    """
    
    html = "<div><p>Hello, <b>world</b>!</p></div>"
    truncator = HTMLTruncator(limit=10)
    truncator.feed(html)
    assert truncator.get_truncated_html() == "<div><p>Hello, <b>wor...</b></p></div>"

def test_handling_unclosed_tags():
    """
    Test case for when truncation is needed with unclosed tags.

    The HTML contains an unclosed tag, and the truncation limit falls before
    the closing tag. The HTML should be truncated and the unclosed tag
    should be properly closed.
    """
    html = "<div><p>Hello, world!"
    truncator = HTMLTruncator(limit=10)
    truncator.feed(html)
    assert truncator.get_truncated_html() == "<div><p>Hello, wor...</p></div>"
