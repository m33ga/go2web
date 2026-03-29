"""Plain-text response parser (pass-through)."""

from go2web.http.parsers import Parser as AbstractParser


class PlainTextParser(AbstractParser):
    """Pass plain-text bodies through with leading/trailing whitespace stripped.

    Example:
        >>> parser = PlainTextParser()
        >>> parser.parse("  hello world  ")
        'hello world'
    """

    def parse(self, body: str) -> str:
        """Return *body* stripped of surrounding whitespace.

        Args:
            body: A plain-text response body.

        Returns:
            The body string with leading and trailing whitespace removed.
        """
        return body.strip()
