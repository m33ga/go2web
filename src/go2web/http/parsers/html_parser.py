"""HTML response parser using BeautifulSoup."""

from bs4 import BeautifulSoup

from go2web.http.parsers import Parser as AbstractParser


class HTMLParser(AbstractParser):
    """Strip HTML markup and return readable plain text.

    Non-content tags (``<script>``, ``<style>``, ``<noscript>``, ``<head>``)
    are removed entirely before text extraction so that rendered output
    contains only visible page content.

    Example:
        >>> parser = HTMLParser()
        >>> parser.parse("<html><body><h1>Hello</h1><p>World</p></body></html>")
        'Hello\\nWorld'
    """

    def parse(self, body: str) -> str:
        """Extract visible text from an HTML document.

        Args:
            body: Raw HTML string.

        Returns:
            Whitespace-normalised plain text with newline separators.
        """
        soup = BeautifulSoup(body, "html.parser")

        # drop non-content tags entirely
        for tag in soup(["script", "style", "noscript", "head"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)

        return text.strip()
