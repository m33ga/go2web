from go2web.console import print_error, print_result
from go2web.http.client import HTTPClient, HTTPError
from go2web.http.parsers import ParserManager
from go2web.http.parsers.exceptions import ParseError


class Fetcher(HTTPClient):
    def fetch(self, url: str) -> str:
        try:
            response = self.get(url)
            parser = ParserManager().get_parser(response.get_content_type())
            text = parser.parse(response.body)
            print_result(text, title=url)
            return text
        except (HTTPError, ParseError) as e:
            print_error(str(e))
            return str(e)
