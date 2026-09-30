"""Parser implementation for Markdown documents."""

from pathlib import Path
import re
from typing import ClassVar, Optional, Tuple

from kbparser.models import Document
from kbparser.parsers.base import BaseParser

_H1_PATTERN = re.compile(r"^#\s+(.+)$", re.MULTILINE)
_H2_PATTERN = re.compile(r"^##\s+(.+)$", re.MULTILINE)
_FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_MD_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\([^)]+\)")
_MD_DECORATION_PATTERN = re.compile(r"[*_`~>#]")


class MarkdownParser(BaseParser):
    """Extracts structured content, headings, and metadata from Markdown files."""

    supported_extensions: ClassVar[Tuple[str, ...]] = ("md", "markdown")

    def parse(self, file_path: Path) -> Document:
        raw_text = self._read_text_safely(file_path)
        frontmatter, body = self._split_frontmatter(raw_text)

        title = self._find_title(frontmatter, body, file_path)
        doc_date = self._find_date(frontmatter, body)
        clean_text = self._clean_markdown(body)
        normalized = self._normalize_text(clean_text)

        word_count = self._count_words(normalized)
        preview = self._extract_preview(normalized)
        doc_id = self._generate_doc_id(file_path)

        metadata = {
            "has_frontmatter": bool(frontmatter),
            "byte_size": file_path.stat().st_size,
        }

        return Document(
            doc_id=doc_id,
            title=title,
            date=doc_date,
            word_count=word_count,
            preview=preview,
            content=normalized,
            format="md",
            source_path=file_path.as_posix(),
            metadata=metadata,
        )

    @classmethod
    def _split_frontmatter(cls, raw: str) -> Tuple[Optional[str], str]:
        match = _FRONTMATTER_PATTERN.match(raw)
        if match:
            return match.group(1), raw[match.end():]
        return None, raw

    @classmethod
    def _find_title(cls, frontmatter: Optional[str], body: str, file_path: Path) -> str:
        if frontmatter:
            for line in frontmatter.splitlines():
                if line.lower().startswith("title:"):
                    return line.split(":", 1)[1].strip().strip("\"'")

        h1 = _H1_PATTERN.search(body)
        if h1:
            return h1.group(1).strip()

        h2 = _H2_PATTERN.search(body)
        if h2:
            return h2.group(1).strip()

        return file_path.stem.replace("_", " ").replace("-", " ").title()

    def _find_date(self, frontmatter: Optional[str], body: str) -> Optional[str]:
        if frontmatter:
            for line in frontmatter.splitlines():
                if line.lower().startswith("date:"):
                    candidate = line.split(":", 1)[1].strip().strip("\"'")
                    parsed = self._extract_date(candidate)
                    if parsed:
                        return parsed
        return self._extract_date(body)

    @classmethod
    def _clean_markdown(cls, text: str) -> str:
        """Strip markdown syntax to obtain clean readable plain text."""
        # Replace links [text](url) with just text
        text = _MD_LINK_PATTERN.sub(r"\1", text)
        # Remove bold, italics, code delimiters, blockquote and heading markers
        text = _MD_DECORATION_PATTERN.sub("", text)
        return text
