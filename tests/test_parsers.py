"""Unit tests for individual format parsers and edge case exceptions."""

from pathlib import Path
import pytest

from kbparser.exceptions import (
    CorruptedFileError,
    EmptyFileError,
    UnsupportedFormatError,
)
from kbparser.parsers.csv import CsvParser
from kbparser.parsers.md import MarkdownParser
from kbparser.parsers.registry import create_default_registry
from kbparser.parsers.txt import TxtParser


def test_txt_parser_standard(sample_archive_dir: Path):
    parser = TxtParser()
    target = sample_archive_dir / "verbale_comitato_sicurezza_2026.txt"
    doc = parser.parse(target)

    assert doc.format == "txt"
    assert "Verbale Riunione Comitato Sicurezza IT" in doc.title
    assert doc.date == "2026-04-10"
    assert doc.word_count > 100
    assert "NIS2" in doc.content
    assert doc.doc_id


def test_txt_parser_legacyprogest(sample_archive_dir: Path):
    parser = TxtParser()
    target = sample_archive_dir / "note_rilascio_legacyprogest.txt"
    doc = parser.parse(target)

    assert doc.format == "txt"
    assert doc.date == "2026-05-18"
    assert "compatibilità" in doc.content or "compatibilit" in doc.content


def test_txt_parser_empty_file(sample_archive_dir: Path):
    parser = TxtParser()
    target = sample_archive_dir / "file_vuoto_zero_bytes.txt"
    with pytest.raises(EmptyFileError):
        parser.parse(target)


def test_markdown_parser_with_frontmatter(sample_archive_dir: Path):
    parser = MarkdownParser()
    target = sample_archive_dir / "incident_postmortem_auth_outage.md"
    doc = parser.parse(target)

    assert doc.format == "md"
    assert "Incident Postmortem" in doc.title
    assert doc.date == "2026-05-02"
    assert "Keycloak" in doc.content
    assert doc.metadata.get("has_frontmatter") is True


def test_markdown_parser_standard(sample_archive_dir: Path):
    parser = MarkdownParser()
    target = sample_archive_dir / "runbook_disaster_recovery_db.md"
    doc = parser.parse(target)

    assert doc.format == "md"
    assert doc.title == "Runbook di Disaster Recovery Database"
    assert doc.date == "2026-03-15"
    assert "PostgreSQL" in doc.content


def test_csv_parser_comma_delimited(sample_archive_dir: Path):
    parser = CsvParser()
    target = sample_archive_dir / "server_inventory_prod.csv"
    doc = parser.parse(target)

    assert doc.format == "csv"
    assert doc.metadata["delimiter"] == ","
    assert doc.metadata["row_count"] >= 7
    assert "srv-db-master" in doc.content
    assert doc.date == "2026-02-20"


def test_csv_parser_semicolon_delimited(sample_archive_dir: Path):
    parser = CsvParser()
    target = sample_archive_dir / "dipendenti_reparti_badge.csv"
    doc = parser.parse(target)

    assert doc.format == "csv"
    assert doc.metadata["delimiter"] == ";"
    assert "EMP-1001" in doc.content


def test_csv_parser_corrupted_file(sample_archive_dir: Path):
    parser = CsvParser()
    target = sample_archive_dir / "export_corrotto_troncato.csv"
    with pytest.raises(CorruptedFileError):
        parser.parse(target)


def test_registry_unsupported_format(sample_archive_dir: Path):
    registry = create_default_registry()
    pdf_target = sample_archive_dir / "template1.pdf"
    with pytest.raises(UnsupportedFormatError):
        registry.get_parser(pdf_target)
