"""Batch execution engine orchestrating folder scanning, parser dispatch, and error handling."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from kbparser.exceptions import ParserError
from kbparser.index import KnowledgeBaseIndex
from kbparser.models import ParseFailure
from kbparser.parsers.registry import ParserRegistry, create_default_registry


@dataclass
class BatchSummary:
    """Summary of batch parsing outcome."""

    total_scanned: int = 0
    indexed_count: int = 0
    failed_count: int = 0
    failures: List[ParseFailure] = field(default_factory=list)

    def print_report(self) -> None:
        """Print a structured textual execution report to stdout."""
        print("=" * 60)
        print("PARSING EXECUTION SUMMARY")
        print("=" * 60)
        print(f"Total files examined:    {self.total_scanned}")
        print(f"Successfully indexed:    {self.indexed_count}")
        print(f"Skipped / Failed files:  {self.failed_count}")
        print("-" * 60)

        if self.failures:
            print("DETAILS OF SKIPPED FILES:")
            for item in self.failures:
                filename = item.file_path.name
                print(f" - [{item.error_type}] {filename}")
                print(f"   Reason: {item.reason}")
            print("-" * 60)
        else:
            print("All examined files processed without errors.")
        print("=" * 60)


class BatchEngine:
    """Dispatches folder contents to registered parsers with error isolation."""

    def __init__(self, registry: Optional[ParserRegistry] = None) -> None:
        self.registry = registry or create_default_registry()

    def process_directory(
        self,
        directory_path: Path,
        index: Optional[KnowledgeBaseIndex] = None,
        recursive: bool = False,
    ) -> BatchSummary:
        """Process all files in the given directory and populate the index."""
        target_dir = Path(directory_path)
        if not target_dir.exists() or not target_dir.is_dir():
            raise FileNotFoundError(f"Target directory not found: {directory_path}")

        kb_index = index if index is not None else KnowledgeBaseIndex()
        summary = BatchSummary()

        pattern = "**/*" if recursive else "*"
        candidates = [p for p in target_dir.glob(pattern) if p.is_file()]
        # Sort candidates deterministically by path
        candidates.sort(key=lambda p: p.as_posix().lower())

        summary.total_scanned = len(candidates)

        for candidate in candidates:
            try:
                parser = self.registry.get_parser(candidate)
                document = parser.parse(candidate)
                kb_index.add(document)
                summary.indexed_count += 1
            except ParserError as err:
                summary.failed_count += 1
                summary.failures.append(
                    ParseFailure(
                        file_path=candidate,
                        reason=str(err),
                        error_type=err.__class__.__name__,
                    )
                )
            except Exception as unhandled:  # Defensive catch for unexpected system faults
                summary.failed_count += 1
                summary.failures.append(
                    ParseFailure(
                        file_path=candidate,
                        reason=f"Unexpected error: {unhandled}",
                        error_type="UnexpectedError",
                    )
                )

        return summary
