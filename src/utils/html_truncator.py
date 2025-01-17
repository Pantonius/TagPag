from html.parser import HTMLParser
import html
from collections import deque

class HTMLTruncator(HTMLParser):
    def __init__(self, limit: int):
        """
        Initialize the HTMLTruncator object.

        :param int limit: The character limit after which the HTML content is truncated.
        """
        
        super().__init__()

        # The character limit for truncation
        self.limit = limit
        
        # List to store the resulting HTML content
        self.result = []
        
        # Counter for the current length of the HTML content
        self.current_length = 0
        
        # Deque to keep track of open HTML tags
        self.open_tags = deque()
        
        # Flag to indicate if truncation has occurred
        self.truncated = False

    def handle_starttag(self, tag, attrs):
        """
        Handle an opening HTML tag.

        Appends the tag and its attributes to the result and stores the tag name in
        the open_tags deque. If the limit has been reached, sets the truncated flag.
        """
        if not self.truncated:
        
            # Append the opening tag to the result
            self.result.append(f"<{tag}")
        
            # Append each attribute of the tag
            for attr, value in attrs:
                self.result.append(f' {attr}="{value}"')
        
            # Close the opening tag
            self.result.append(">")
        
            # Store the tag name in the deque
            self.open_tags.appendleft(tag)

    def handle_endtag(self, tag):
        """
        Handle a closing HTML tag.

        If the tag is at the top of the open_tags deque and the truncation limit
        has not been reached, appends the closing tag to the result and removes
        the tag from the deque.
        """
        if not self.truncated:
            # Check if the tag is the last opened tag

            if self.open_tags and self.open_tags[0] == tag:
            
                # Append the closing tag to the result
                self.result.append(f"</{tag}>")
            
                # Remove the tag from the deque
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

        # Check if adding the data exceeds the limit
        if self.current_length + len(data) > self.limit:

            # Calculate remaining characters allowed
            remaining = self.limit - self.current_length
            
            # Append truncated data with ellipsis
            self.result.append(html.escape(data[:remaining]) + "...")
            
            # Update the current length to the limit
            self.current_length = self.limit
            
            # Set the truncated flag
            self.truncated = True
        else:
            
            # Append the data to the result
            self.result.append(html.escape(data))
            
            # Update the current length
            self.current_length += len(data)

    def get_truncated_html(self):
        """
        Return the truncated HTML content as a string.

        Closes any unclosed tags left open by the truncation process and returns
        the resulting HTML string.
        """
        
        # Close any unclosed tags
        for tag in self.open_tags:
            self.result.append(f"</{tag}>")
        
        # Join the result list into a single string and return it
        return "".join(self.result)