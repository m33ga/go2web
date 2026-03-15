from go2web.http.client import HTTPClient
from go2web.http.parsers import ParserManager
from go2web.http.parsers.exceptions import UnsupportedContentTypeError


class Fetcher(HTTPClient):
    def fetch(self, url: str) -> str:
        response = self.get(url)
        try:
            parser = ParserManager().get_parser(response.get_content_type())
            return parser.parse(response.body)
        except UnsupportedContentTypeError:
            return "Server returned unsupported content type"
