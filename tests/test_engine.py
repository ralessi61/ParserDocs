"""Integration tests for BatchEngine error handling and archive scanning."""

from pathlib import Path

from kbparser.engine import BatchEngine
from kbparser.index import KnowledgeBaseIndex


def test_batch_engine_sample_archive(sample_archive_dir: Path):
    engine = BatchEngine()
    index = KnowledgeBaseIndex()

    summary = engine.process_directory(sample_archive_dir, index=index)

    # 16 total files in sample_archive
    assert summary.total_scanned == 16

    # 4 expected failures:
    # 1. file_vuoto_zero_bytes.txt (EmptyFileError)
    # 2. export_corrotto_troncato.csv (CorruptedFileError)
    # 3. template1.pdf (UnsupportedFormatError)
    # 4. backup_dump_2026.bak (UnsupportedFormatError)
    assert summary.failed_count == 4
    assert summary.indexed_count == 12
    assert len(index) == 12

    # Check that failed files are properly recorded
    failed_names = {f.file_path.name for f in summary.failures}
    assert "file_vuoto_zero_bytes.txt" in failed_names
    assert "export_corrotto_troncato.csv" in failed_names
    assert "template1.pdf" in failed_names
    assert "backup_dump_2026.bak" in failed_names

    # Check search over indexed archive
    results = index.search("PostgreSQL")
    assert len(results) >= 2  # runbook and postmortem or SAN specs
