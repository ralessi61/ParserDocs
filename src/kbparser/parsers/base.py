"""Abstract base class and core utilities for document parsers."""

from abc import ABC, abstractmethod
import hashlib
from pathlib import Path
import re
from typing import ClassVar, Optional, Tuple

from kbparser.exceptions import (
    CorruptedFileError,
    EmptyFileError,
    FileAccessError,
)
from kbparser.models import Document

_DATE_PATTERNS = (
    re.compile(r"\b(20\d\d[-/.](?:0[1-9]|1[0-2])[-/.](?:0[1-9]|[12]\d|3[01]))\b"),
    re.compile(r"\b((?:0[1-9]|[12]\d|3[01])[-/.](?:0[1-9]|1[0-2])[-/.]20\d\d)\b"),
)


class BaseParser(ABC):
    """Abstract interface defining the contract for all format-specific parsers."""

    supported_extensions: ClassVar[Tuple[str, ...]] = ()

    @classmethod
    def can_handle(cls, file_path: Path) -> bool:
        """Return True if this parser supports the target file's extension."""
        suffix = file_path.suffix.lower().lstrip(".")
        return suffix in cls.supported_extensions

    @abstractmethod
    def parse(self, file_path: Path) -> Document:
        """Parse the given file and return a normalized Document instance.

        Raises:
            EmptyFileError: When file is empty.
            CorruptedFileError: When contents are unreadable or invalid.
            FileAccessError: When reading fails due to OS permissions.
        """
        pass

    @staticmethod
    def _read_text_safely(file_path: Path) -> str:
        """Read text handling BOMs and common legacy encodings gracefully."""
        try:
            stat = file_path.stat()
            if stat.st_size == 0:
                raise EmptyFileError("File is empty (0 bytes)", file_path)

            raw_bytes = file_path.read_bytes()
            if not raw_bytes or raw_bytes.isspace():
                raise EmptyFileError("File contains only whitespace", file_path)

            for encoding in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
                try:
                    return raw_bytes.decode(encoding)
                except (UnicodeDecodeError, LookupError):
                    continue

            raise CorruptedFileError("Unable to decode text with supported encodings", file_path)
        except (PermissionError, OSError) as exc:
            if isinstance(exc, (EmptyFileError, CorruptedFileError)):
                raise
            raise FileAccessError(f"I/O error reading file: {exc}", file_path) from exc

    @staticmethod
    def _extract_date(text: str) -> Optional[str]:
        """Attempt to extract an ISO-like or European date string from text."""
        for pattern in _DATE_PATTERNS:
            match = pattern.search(text)
            if match:
                raw_date = match.group(1).replace("/", "-").replace(".", "-")
                parts = raw_date.split("-")
                if len(parts[0]) == 4:
                    return f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
                return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
        return None

    @staticmethod
    def _generate_doc_id(file_path: Path) -> str:
        """Generate a short deterministic ID based on the file path."""
        normalized = file_path.as_posix().lower()
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize line endings and collapse excessive blank lines."""
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        lines = [line.strip() for line in text.splitlines()]
        cleaned = "\n".join(lines)
        return re.sub(r"\n{3,}", "\n\n", cleaned).strip()

    @staticmethod
    def _extract_preview(text: str, max_chars: int = 200) -> str:
        """Produce a clean summary preview truncated at word boundary."""
        single_line = re.sub(r"\s+", " ", text).strip()
        if len(single_line) <= max_chars:
            return single_line
        truncated = single_line[:max_chars]
        last_space = truncated.rfind(" ")
        if last_space > 0:
            truncated = truncated[:last_space]
        return f"{truncated}..."

    @staticmethod
    def _count_words(text: str) -> int:
        """Count words using Unicode word boundaries."""
        return len(re.findall(r"\b\w+\b", text, re.UNICODE))
