"""Registry that maps content-type strings to :class:`~go2web.http.parsers.abstract_parser.Parser` instances."""

from go2web.http.parsers import Parser
from go2web.http.parsers.exceptions import ParseError
from go2web.http.parsers.html_parser import HTMLParser
from go2web.http.parsers.json_parser import JSONParser
from go2web.http.parsers.plain_text_parser import PlainTextParser


class ParserManager:
    """Maps ``Content-Type`` values to the appropriate :class:`~go2web.http.parsers.abstract_parser.Parser`.

    The registry performs a case-insensitive substring match, so
    ``"text/html; charset=utf-8"`` correctly resolves to :class:`~go2web.http.parsers.html_parser.HTMLParser`.

    Built-in registry:

    | Content-Type | Parser |
    |---|---|
    | ``text/html`` | :class:`~go2web.http.parsers.html_parser.HTMLParser` |
    | ``application/json`` | :class:`~go2web.http.parsers.json_parser.JSONParser` |
    | ``text/plain`` | :class:`~go2web.http.parsers.plain_text_parser.PlainTextParser` |

    Example:
        >>> from go2web.http.parsers.parser_manager import ParserManager
        >>> manager = ParserManager()
        >>> parser = manager.get_parser("application/json; charset=utf-8")
        >>> parser.parse('{"key": "value"}')
        '{\\n  "key": "value"\\n}'
    """

    _REGISTRY: dict[str, Parser] = {
        "text/html": HTMLParser(),
        "application/json": JSONParser(),
        "text/plain": PlainTextParser(),
    }

    def get_parser(self, content_type: str) -> Parser:
        """Return the parser for *content_type*.

        Args:
            content_type: The value of the ``Content-Type`` response header,
                e.g. ``"text/html; charset=utf-8"``.

        Returns:
            A :class:`~go2web.http.parsers.abstract_parser.Parser` instance.

        Raises:
            ~go2web.http.parsers.exceptions.ParseError: When no parser is
                registered for *content_type*.
        """
        for ct, parser in self._REGISTRY.items():
            if ct.lower() in content_type.lower():
                return parser
        raise ParseError(f"Error: Cant find parser for: {content_type} (for now)")
