"""Abstract base class for content-type parsers."""

from abc import ABC, abstractmethod


class Parser(ABC):
    """Abstract base class for response body parsers.

    Subclasses implement :meth:`parse` to transform a raw response body string
    into a human-readable representation suitable for terminal output.

    To add a new content type, subclass :class:`Parser` and register the
    instance in :class:`~go2web.http.parsers.parser_manager.ParserManager`.
    """

    @abstractmethod
    def parse(self, body: str) -> str:
        """Parse *body* and return a human-readable string.

        Args:
            body: The raw response body decoded from bytes.

        Returns:
            A cleaned, human-readable representation of *body*.

        Raises:
            ~go2web.http.parsers.exceptions.ParseError: When the body cannot
                be interpreted as the expected format.
        """
        ...
