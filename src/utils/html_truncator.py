from html.parser import HTMLParser
from collections import deque

class HTMLTruncator(HTMLParser):
    def __init__(self, limit: int):
        """
        Initialize the HTMLTruncator object.

        :param int limit: The character limit after which the HTML content is truncated.
        """
        super().__init__()
        self.limit = limit
        self.result = []
        self.current_length = 0
        self.open_tags = deque()
        self.truncated = False

    def handle_starttag(self, tag, attrs):
        """
        Handle an opening HTML tag.

        Appends the tag and its attributes to the result and stores the tag name in
        the open_tags deque. If the limit has been reached, sets the truncated flag.
        """
        if not self.truncated:
            self.result.append(f"<{tag}")
            for attr, value in attrs:
                self.result.append(f' {attr}="{value}"')
            self.result.append(">")
            self.open_tags.appendleft(tag)

    def handle_endtag(self, tag):
        """
        Handle a closing HTML tag.

        If the tag is at the top of the open_tags deque and the truncation limit
        has not been reached, appends the closing tag to the result and removes
        the tag from the deque.
        """
        if not self.truncated:
            if self.open_tags and self.open_tags[0] == tag:
                self.result.append(f"</{tag}>")
                self.open_tags.popleft()

    def handle_data(self, data):
        """
        Handle HTML data (text, CDATA, etc.).

        If the truncation limit has not been reached, appends the data to the result
        and increments the current length. If the limit has been reached, truncates
        the data, appends it to the result, and sets the truncated flag.
        """
        if self.truncated:
            return

        if self.current_length + len(data) > self.limit:
            remaining = self.limit - self.current_length
            self.result.append(data[:remaining] + "...")
            self.current_length = self.limit
            self.truncated = True
        else:
            self.result.append(data)
            self.current_length += len(data)

    def get_truncated_html(self):
        """
        Return the truncated HTML content as a string.

        Closes any unclosed tags left open by the truncation process and returns
        the resulting HTML string.
        """
        for tag in self.open_tags:
            self.result.append(f"</{tag}>")
        return "".join(self.result)
