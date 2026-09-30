"""Pytest fixtures for testing parsers and knowledge base indexing."""

from pathlib import Path
import pytest

from kbparser.models import Document


@pytest.fixture
def sample_archive_dir() -> Path:
    """Return path to the sample_archive directory."""
    return Path(__file__).resolve().parent.parent / "sample_archive"


@pytest.fixture
def sample_document() -> Document:
    """Provide a mock Document instance for index tests."""
    return Document(
        doc_id="test12345678",
        title="Sample Test Document",
        date="2026-05-10",
        word_count=42,
        preview="Sample preview text for testing purposes.",
        content="This is the normalized body content containing keywords like database and security.",
        format="txt",
        source_path="sample/test.txt",
        metadata={"byte_size": 256},
    )
