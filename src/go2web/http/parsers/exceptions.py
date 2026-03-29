"""Exceptions raised by content-type parsers."""


class ParseError(Exception):
    """Raised when a parser cannot interpret a response body.

    Typically caught by :class:`~go2web.commands.fetch.Fetcher` and displayed
    as a styled error panel in the terminal.
    """
