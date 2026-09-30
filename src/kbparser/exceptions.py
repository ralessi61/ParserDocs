"""Custom exception hierarchy for the parser and knowledge base."""

from pathlib import Path
from typing import Optional


class ParserError(Exception):
    """Base exception for all parsing and indexing failures."""

    def __init__(self, message: str, file_path: Optional[Path] = None):
        super().__init__(message)
        self.file_path = file_path
        self.message = message

    def __str__(self) -> str:
        if self.file_path:
            return f"[{self.file_path.name}] {self.message}"
        return self.message


class UnsupportedFormatError(ParserError):
    """Raised when encountering a file format with no registered parser."""
    pass


class EmptyFileError(ParserError):
    """Raised when a candidate document contains zero bytes or only whitespace."""
    pass


class CorruptedFileError(ParserError):
    """Raised when file content cannot be parsed due to structure or encoding issues."""
    pass


class FileAccessError(ParserError):
    """Raised when filesystem permissions prevent reading a document."""
    pass
