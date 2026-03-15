from go2web.http.parsers import HTMLParser, JSONParser, Parser
from go2web.http.parsers.exceptions import ParseError


class ParserManager:
    _REGISTRY: dict[str, Parser] = {
        "text/html": HTMLParser(),
        "application/json": JSONParser(),
    }

    def get_parser(self, content_type: str) -> Parser:
        for ct, parser in self._REGISTRY.items():
            if ct.lower() in content_type.lower():
                return parser
        raise ParseError(f"Error: Cant find parser for: {content_type} (for now)")
