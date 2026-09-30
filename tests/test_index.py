"""Unit tests for KnowledgeBaseIndex operations, queries, and serialization."""

from pathlib import Path

from kbparser.index import KnowledgeBaseIndex
from kbparser.models import Document


def test_index_add_and_list(sample_document: Document):
    index = KnowledgeBaseIndex()
    assert len(index) == 0

    index.add(sample_document)
    assert len(index) == 1

    docs = index.list_documents()
    assert len(docs) == 1
    assert docs[0].doc_id == sample_document.doc_id


def test_index_search(sample_document: Document):
    index = KnowledgeBaseIndex()
    index.add(sample_document)

    # Search in title
    res_title = index.search("Sample")
    assert len(res_title) == 1

    # Search in content
    res_content = index.search("database")
    assert len(res_content) == 1

    # Search non-matching term
    res_none = index.search("nonexistentkeyword")
    assert len(res_none) == 0


def test_index_filter_by_format(sample_document: Document):
    index = KnowledgeBaseIndex()
    index.add(sample_document)

    txt_docs = index.filter_by_format("txt")
    assert len(txt_docs) == 1

    md_docs = index.filter_by_format("md")
    assert len(md_docs) == 0


def test_index_statistics(sample_document: Document):
    index = KnowledgeBaseIndex()
    index.add(sample_document)

    stats = index.get_statistics()
    assert stats["total_documents"] == 1
    assert stats["formats"]["txt"] == 1
    assert stats["total_words"] == sample_document.word_count
    assert stats["dates"]["earliest"] == "2026-05-10"


def test_index_json_roundtrip(tmp_path: Path, sample_document: Document):
    index = KnowledgeBaseIndex()
    index.add(sample_document)

    save_path = tmp_path / "test_index.json"
    index.save_to_json(save_path)
    assert save_path.exists()

    loaded = KnowledgeBaseIndex.load_from_json(save_path)
    assert len(loaded) == 1
    loaded_doc = loaded.get(sample_document.doc_id)
    assert loaded_doc is not None
    assert loaded_doc.title == sample_document.title
    assert loaded_doc.content == sample_document.content
