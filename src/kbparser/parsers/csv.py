"""Parser implementation for comma-separated and delimited tabular files."""

import csv
import io
from pathlib import Path
from typing import ClassVar, List, Optional, Tuple

from kbparser.exceptions import CorruptedFileError, EmptyFileError
from kbparser.models import Document
from kbparser.parsers.base import BaseParser


class CsvParser(BaseParser):
    """Parses delimited tabular files into search-friendly document representations."""

    supported_extensions: ClassVar[Tuple[str, ...]] = ("csv",)

    def parse(self, file_path: Path) -> Document:
        raw_text = self._read_text_safely(file_path)
        delimiter = self._sniff_delimiter(raw_text, file_path)

        rows = self._read_rows(raw_text, delimiter, file_path)
        if not rows:
            raise EmptyFileError("CSV contains no valid data rows", file_path)

        headers = [h.strip() for h in rows[0]]
        data_rows = rows[1:]

        title = self._derive_title(headers, file_path)
        doc_date = self._find_date_in_cells(rows)
        content = self._build_searchable_representation(headers, data_rows)
        normalized = self._normalize_text(content)

        word_count = self._count_words(normalized)
        preview = self._extract_preview(normalized)
        doc_id = self._generate_doc_id(file_path)

        metadata = {
            "columns": headers,
            "column_count": len(headers),
            "row_count": len(data_rows),
            "delimiter": delimiter,
            "byte_size": file_path.stat().st_size,
        }

        return Document(
            doc_id=doc_id,
            title=title,
            date=doc_date,
            word_count=word_count,
            preview=preview,
            content=normalized,
            format="csv",
            source_path=file_path.as_posix(),
            metadata=metadata,
        )

    @classmethod
    def _sniff_delimiter(cls, sample: str, file_path: Path) -> str:
        """Infer delimiter using Sniffer, falling back to frequency analysis."""
        lines = [line for line in sample.splitlines() if line.strip()][:10]
        if not lines:
            return ","

        sample_subset = "\n".join(lines)
        try:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample_subset, delimiters=",;\t|")
            return dialect.delimiter
        except csv.Error:
            # Fallback heuristic
            first_line = lines[0]
            counts = {sep: first_line.count(sep) for sep in (",", ";", "\t", "|")}
            best = max(counts, key=counts.get)
            return best if counts[best] > 0 else ","

    @classmethod
    def _read_rows(cls, raw: str, delimiter: str, file_path: Path) -> List[List[str]]:
        try:
            reader = csv.reader(io.StringIO(raw), delimiter=delimiter)
            rows = [row for row in reader if any(cell.strip() for cell in row)]
            if rows:
                expected_cols = len(rows[0])
                if expected_cols > 1 and len(rows) > 2:
                    mismatched = sum(1 for r in rows[1:] if len(r) != expected_cols)
                    if mismatched / (len(rows) - 1) >= 0.5:
                        raise CorruptedFileError(
                            f"Corrupted tabular structure: {mismatched} rows have irregular column counts",
                            file_path,
                        )
            return rows
        except csv.Error as exc:
            raise CorruptedFileError(f"Malformed CSV formatting: {exc}", file_path) from exc

    @classmethod
    def _derive_title(cls, headers: List[str], file_path: Path) -> str:
        stem_title = file_path.stem.replace("_", " ").replace("-", " ").title()
        if headers:
            joined_headers = ", ".join(headers[:4])
            return f"{stem_title} ({joined_headers})"
        return stem_title

    def _find_date_in_cells(self, rows: List[List[str]]) -> Optional[str]:
        # Inspect up to first 25 rows for any date
        for row in rows[:25]:
            for cell in row:
                detected = self._extract_date(cell)
                if detected:
                    return detected
        return None

    @classmethod
    def _build_searchable_representation(cls, headers: List[str], data_rows: List[List[str]]) -> str:
        """Build structured, readable summary text indexed for keyword searching."""
        lines = []
        if headers:
            lines.append(f"Tabular Dataset Columns: {', '.join(headers)}")
            lines.append(f"Total Rows: {len(data_rows)}")
            lines.append("")

        for idx, row in enumerate(data_rows, start=1):
            cell_descriptions = []
            for col_idx, cell in enumerate(row):
                if not cell.strip():
                    continue
                header_name = headers[col_idx] if col_idx < len(headers) else f"Col_{col_idx+1}"
                cell_descriptions.append(f"{header_name}: {cell.strip()}")
            if cell_descriptions:
                lines.append(f"Record {idx}: " + " | ".join(cell_descriptions))

        return "\n".join(lines)