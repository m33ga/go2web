"""JSON response parser."""

import json

from go2web.http.parsers import Parser as AbstractParser
from go2web.http.parsers.exceptions import ParseError


class JSONParser(AbstractParser):
    """Parse a JSON response body and return it pretty-printed.

    Example:
        >>> parser = JSONParser()
        >>> parser.parse('{"name":"go2web","version":"0.1.0"}')
        '{\\n  "name": "go2web",\\n  "version": "0.1.0"\\n}'
    """

    def parse(self, body: str) -> str:
        """Deserialise *body* and return it indented with two spaces.

        Args:
            body: A JSON-encoded string.

        Returns:
            Pretty-printed JSON with ``ensure_ascii=False`` so Unicode
            characters are preserved.

        Raises:
            ~go2web.http.parsers.exceptions.ParseError: When *body* is not
                valid JSON.
        """
        try:
            data = json.loads(body)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except json.JSONDecodeError as e:
            raise ParseError("Error: Bad Jayson or content encoding") from e
