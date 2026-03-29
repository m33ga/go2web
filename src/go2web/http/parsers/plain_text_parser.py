from go2web.http.parsers import Parser as AbstractParser


class PlainTextParser(AbstractParser):
    """Pass plain-text bodies through unchanged."""

    def parse(self, body: str) -> str:
        return body.strip()
