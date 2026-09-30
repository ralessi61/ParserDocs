"""Parser implementation for plain text documents."""

from pathlib import Path
from typing import ClassVar, Tuple

from kbparser.models import Document
from kbparser.parsers.base import BaseParser


class TxtParser(BaseParser):
    """Parses plain text files into canonical Document representations."""

    supported_extensions: ClassVar[Tuple[str, ...]] = ("txt",)

    def parse(self, file_path: Path) -> Document:
        raw_text = self._read_text_safely(file_path)
        content = self._normalize_text(raw_text)

        title = self._extract_title(content, file_path)
        doc_date = self._extract_date(content)
        word_count = self._count_words(content)
        preview = self._extract_preview(content)
        doc_id = self._generate_doc_id(file_path)

        return Document(
            doc_id=doc_id,
            title=title,
            date=doc_date,
            word_count=word_count,
            preview=preview,
            content=content,
            format="txt",
            source_path=file_path.as_posix(),
            metadata={"byte_size": file_path.stat().st_size},
        )

    @staticmethod
    def _extract_title(content: str, file_path: Path) -> str:
        for line in content.splitlines():
            stripped = line.strip()
            if stripped and len(stripped) <= 120:
                # Discard purely numeric or symbol-heavy lines as headers
                if any(char.isalpha() for char in stripped):
                    return stripped
        # Fallback to humanized filename stem
        return file_path.stem.replace("_", " ").replace("-", " ").title()
