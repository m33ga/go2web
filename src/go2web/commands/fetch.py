from go2web.http.client import HTTPClient, HTTPError
from go2web.http.parsers import ParserManager
from go2web.http.parsers.exceptions import ParseError


class Fetcher(HTTPClient):
    def fetch(self, url: str) -> str:
        try:
            response = self.get(url)
            parser = ParserManager().get_parser(response.get_content_type())
            return parser.parse(response.body)
        except (HTTPError, ParseError) as e:
            return str(e)
