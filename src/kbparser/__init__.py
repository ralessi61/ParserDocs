"""Knowledge Base Parser & Indexer package."""

from kbparser.engine import BatchEngine, BatchSummary
from kbparser.exceptions import (
    CorruptedFileError,
    EmptyFileError,
    FileAccessError,
    ParserError,
    UnsupportedFormatError,
)
from kbparser.index import KnowledgeBaseIndex
from kbparser.models import Document, ParseFailure
from kbparser.parsers import (
    BaseParser,
    CsvParser,
    MarkdownParser,
    ParserRegistry,
    TxtParser,
    create_default_registry,
)

__version__ = "0.1.0"
__all__ = [
    "BatchEngine",
    "BatchSummary",
    "CorruptedFileError",
    "Document",
    "EmptyFileError",
    "FileAccessError",
    "KnowledgeBaseIndex",
    "ParseFailure",
    "ParserError",
    "ParserRegistry",
    "UnsupportedFormatError",
    "BaseParser",
    "CsvParser",
    "MarkdownParser",
    "TxtParser",
    "create_default_registry",
]
