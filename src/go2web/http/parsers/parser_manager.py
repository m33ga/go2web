from go2web.http.parsers import Parser
from go2web.http.parsers.exceptions import ParseError
from go2web.http.parsers.html_parser import HTMLParser
from go2web.http.parsers.json_parser import JSONParser
from go2web.http.parsers.plain_text_parser import PlainTextParser


class ParserManager:
    _REGISTRY: dict[str, Parser] = {
        "text/html": HTMLParser(),
        "application/json": JSONParser(),
        "text/plain": PlainTextParser(),
    }

    def get_parser(self, content_type: str) -> Parser:
        for ct, parser in self._REGISTRY.items():
            if ct.lower() in content_type.lower():
                return parser
        raise ParseError(f"Error: Cant find parser for: {content_type} (for now)")
