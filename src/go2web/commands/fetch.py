from go2web.http.client import HTTPClient, Response


class Fetcher(HTTPClient):
    def fetch(self, url: str) -> Response:
        return self.get(url)
