"""Knowledge Base Index maintaining in-memory documents with search and persistence."""

from collections import Counter
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from kbparser.models import Document


class KnowledgeBaseIndex:
    """In-memory searchable catalog of normalized documents."""

    def __init__(self) -> None:
        self._documents: Dict[str, Document] = {}
        self._format_index: Dict[str, List[str]] = {}

    def __len__(self) -> int:
        return len(self._documents)

    def add(self, doc: Document) -> None:
        """Add a normalized document to the index."""
        self._documents[doc.doc_id] = doc
        fmt = doc.format.lower()
        if fmt not in self._format_index:
            self._format_index[fmt] = []
        if doc.doc_id not in self._format_index[fmt]:
            self._format_index[fmt].append(doc.doc_id)

    def get(self, doc_id: str) -> Optional[Document]:
        """Fetch a document by its unique ID."""
        return self._documents.get(doc_id)

    def list_documents(self) -> List[Document]:
        """Return all documents ordered by title."""
        return sorted(self._documents.values(), key=lambda d: d.title.lower())

    def filter_by_format(self, format_name: str) -> List[Document]:
        """Return documents matching a specific file format."""
        norm_fmt = format_name.lower().lstrip(".")
        doc_ids = self._format_index.get(norm_fmt, [])
        return [self._documents[did] for did in doc_ids if did in self._documents]

    def search(
        self,
        query: str,
        in_title: bool = True,
        in_content: bool = True,
        case_sensitive: bool = False,
    ) -> List[Document]:
        """Search documents by keyword across title and/or content."""
        if not query.strip():
            return []

        search_term = query if case_sensitive else query.lower()
        results: List[Document] = []

        for doc in self._documents.values():
            matched = False
            if in_title:
                haystack = doc.title if case_sensitive else doc.title.lower()
                if search_term in haystack:
                    matched = True

            if not matched and in_content:
                haystack = doc.content if case_sensitive else doc.content.lower()
                if search_term in haystack:
                    matched = True

            if matched:
                results.append(doc)

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Compute aggregate statistics of the indexed documents."""
        if not self._documents:
            return {
                "total_documents": 0,
                "formats": {},
                "total_words": 0,
                "average_words": 0.0,
                "longest_documents": [],
                "dates": {"earliest": None, "latest": None},
            }

        docs = list(self._documents.values())
        counts_by_format = dict(Counter(d.format for d in docs))
        total_words = sum(d.word_count for d in docs)
        avg_words = round(total_words / len(docs), 1)

        sorted_by_length = sorted(docs, key=lambda d: d.word_count, reverse=True)
        top_longest = [
            {"title": d.title, "format": d.format, "words": d.word_count, "doc_id": d.doc_id}
            for d in sorted_by_length[:5]
        ]

        valid_dates = sorted([d.date for d in docs if d.date])
        earliest_date = valid_dates[0] if valid_dates else None
        latest_date = valid_dates[-1] if valid_dates else None

        return {
            "total_documents": len(docs),
            "formats": counts_by_format,
            "total_words": total_words,
            "average_words": avg_words,
            "longest_documents": top_longest,
            "dates": {"earliest": earliest_date, "latest": latest_date},
        }

    def save_to_json(self, file_path: Path) -> None:
        """Serialize index contents to a readable JSON file."""
        payload = {
            "version": "1.0",
            "document_count": len(self._documents),
            "documents": [doc.to_dict() for doc in self.list_documents()],
        }
        target = Path(file_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_json(cls, file_path: Path) -> "KnowledgeBaseIndex":
        """Instantiate a KnowledgeBaseIndex from a previously exported JSON file."""
        target = Path(file_path)
        with open(target, "r", encoding="utf-8") as f:
            payload = json.load(f)

        index = cls()
        for doc_dict in payload.get("documents", []):
            doc = Document.from_dict(doc_dict)
            index.add(doc)
        return index
