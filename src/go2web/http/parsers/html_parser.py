from bs4 import BeautifulSoup

from go2web.http.parsers import Parser as AbstractParser


class HTMLParser(AbstractParser):
    def parse(self, body: str) -> str:
        soup = BeautifulSoup(body, "html.parser")

        # drop non-content tags entirely
        for tag in soup(["script", "style", "noscript", "head"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)

        return text.strip()
