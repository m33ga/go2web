# Content parsers

Parsers transform raw response bodies into readable text.
`ParserManager` picks the right parser from the `Content-Type` header;
each concrete parser handles one media type.

## ParserManager

::: go2web.http.parsers.parser_manager.ParserManager

## HTMLParser

::: go2web.http.parsers.html_parser.HTMLParser

## JSONParser

::: go2web.http.parsers.json_parser.JSONParser

## PlainTextParser

::: go2web.http.parsers.plain_text_parser.PlainTextParser

## Parser *(abstract)*

::: go2web.http.parsers.abstract_parser.Parser

## ParseError

::: go2web.http.parsers.exceptions.ParseError
