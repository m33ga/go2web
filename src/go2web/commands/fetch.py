"""High-level fetch command — wraps :class:`~go2web.http.client.HTTPClient` with terminal output."""

from go2web.console import print_error, print_result
from go2web.http.client import HTTPClient, HTTPError
from go2web.http.parsers import ParserManager
from go2web.http.parsers.exceptions import ParseError


class Fetcher(HTTPClient):
    """Fetch a URL and print the parsed response to the terminal.

    Inherits from :class:`~go2web.http.client.HTTPClient` so all constructor
    arguments (``cache``, ``use_cache``) are available.

    The response body is parsed by the appropriate
    :class:`~go2web.http.parsers.abstract_parser.Parser` for its content type,
    then displayed inside a styled Rich panel. Errors are caught and printed
    as red error panels rather than propagating as exceptions.

    Example:
        >>> from go2web.commands.fetch import Fetcher
        >>> fetcher = Fetcher(use_cache=False)
        >>> text = fetcher.fetch("https://example.com")
    """

    def fetch(self, url: str) -> str:
        """Fetch *url*, parse the body, and print it to stdout.

        Args:
            url: The URL to fetch. A missing ``https://`` scheme is added
                automatically by the underlying :class:`~go2web.http.client.HTTPClient`.

        Returns:
            The parsed body string on success, or the error message string
            when an :class:`~go2web.http.client.HTTPError` or
            :class:`~go2web.http.parsers.exceptions.ParseError` is raised.
        """
        try:
            response = self.get(url)
            parser = ParserManager().get_parser(response.get_content_type())
            text = parser.parse(response.body)
            print_result(text, title=url)
            return text
        except (HTTPError, ParseError) as e:
            print_error(str(e))
            return str(e)
