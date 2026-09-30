"""Data models representing normalized documents and batch execution state."""

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class Document:
    """Canonical representation of an ingested document across all source formats."""

    doc_id: str
    title: str
    date: Optional[str]
    word_count: int
    preview: str
    content: str
    format: str
    source_path: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize document to a dictionary suitable for JSON dumping."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Document":
        """Reconstruct a Document instance from a deserialized dictionary."""
        return cls(
            doc_id=data["doc_id"],
            title=data["title"],
            date=data.get("date"),
            word_count=int(data["word_count"]),
            preview=data["preview"],
            content=data["content"],
            format=data["format"],
            source_path=data["source_path"],
            metadata=data.get("metadata", {}),
        )


@dataclass
class ParseFailure:
    """Detailed record of a file that could not be parsed."""

    file_path: Path
    reason: str
    error_type: str
