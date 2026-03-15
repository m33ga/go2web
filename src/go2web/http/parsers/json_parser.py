from go2web.http.parsers import Parser as AbstractParser


class JSONParser(AbstractParser):
    def parse(self, body: str) -> str:
        return ""
