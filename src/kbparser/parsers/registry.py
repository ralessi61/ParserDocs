"""Registry providing dynamic dispatch to parsers based on file extensions."""

from pathlib import Path
from typing import Dict, List, Type

from kbparser.exceptions import UnsupportedFormatError
from kbparser.parsers.base import BaseParser
from kbparser.parsers.csv import CsvParser
from kbparser.parsers.md import MarkdownParser
from kbparser.parsers.txt import TxtParser


class ParserRegistry:
    """Manages format-specific parsers following the Open/Closed Principle."""

    def __init__(self) -> None:
        self._parsers: Dict[str, BaseParser] = {}

    def register(self, parser_class: Type[BaseParser]) -> None:
        """Register a parser class for its declared extensions."""
        instance = parser_class()
        for ext in parser_class.supported_extensions:
            normalized_ext = ext.lower().lstrip(".")
            self._parsers[normalized_ext] = instance

    def get_parser(self, file_path: Path) -> BaseParser:
        """Locate appropriate parser instance or raise UnsupportedFormatError."""
        ext = file_path.suffix.lower().lstrip(".")
        if not ext or ext not in self._parsers:
            raise UnsupportedFormatError(
                f"No parser registered for extension '{file_path.suffix}'",
                file_path=file_path,
            )
        return self._parsers[ext]

    def supported_extensions(self) -> List[str]:
        """Return sorted list of currently registered file extensions."""
        return sorted(self._parsers.keys())


def create_default_registry() -> ParserRegistry:
    """Instantiate and configure standard parser registry."""
    registry = ParserRegistry()
    registry.register(TxtParser)
    registry.register(MarkdownParser)
    registry.register(CsvParser)
    return registry
