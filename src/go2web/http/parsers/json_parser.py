import json

from go2web.http.parsers import Parser as AbstractParser
from go2web.http.parsers.exceptions import ParseError


class JSONParser(AbstractParser):
    def parse(self, body: str) -> str:
        try:
            data = json.loads(body)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except json.JSONDecodeError as e:
            raise ParseError("Error: Bad Jayson or content encoding") from e
