"""Command-line interface for the knowledge base document parser and indexer."""

import argparse
from pathlib import Path
import sys
from typing import Optional

from kbparser.engine import BatchEngine
from kbparser.index import KnowledgeBaseIndex


def cmd_build(args: argparse.Namespace) -> int:
    """Scan folder, parse supported documents, output summary report and save index."""
    input_dir = Path(args.directory)
    if not input_dir.exists():
        print(f"Error: Directory '{args.directory}' does not exist.", file=sys.stderr)
        return 1

    engine = BatchEngine()
    index = KnowledgeBaseIndex()

    summary = engine.process_directory(input_dir, index=index, recursive=args.recursive)
    summary.print_report()

    output_path = Path(args.output)
    index.save_to_json(output_path)
    print(f"\nKnowledge base index saved to: {output_path.resolve()}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    """Search documents in an existing index by keyword."""
    index_path = Path(args.index)
    if not index_path.exists():
        print(f"Error: Index file '{args.index}' does not exist.", file=sys.stderr)
        return 1

    index = KnowledgeBaseIndex.load_from_json(index_path)

    results = index.search(
        query=args.query,
        in_title=not args.content_only,
        in_content=not args.title_only,
        case_sensitive=args.case_sensitive,
    )

    if args.format:
        fmt = args.format.lower().lstrip(".")
        results = [d for d in results if d.format == fmt]

    print(f"Found {len(results)} matching document(s) for query: '{args.query}'\n")
    for idx, doc in enumerate(results, start=1):
        print(f"[{idx}] {doc.title}")
        print(f"    ID:       {doc.doc_id}")
        print(f"    Format:   {doc.format.upper()} | Words: {doc.word_count} | Date: {doc.date or 'N/A'}")
        print(f"    Path:     {doc.source_path}")
        if args.preview or args.verbose:
            print(f"    Preview:  {doc.preview}")
        print()
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    """List indexed documents."""
    index_path = Path(args.index)
    if not index_path.exists():
        print(f"Error: Index file '{args.index}' does not exist.", file=sys.stderr)
        return 1

    index = KnowledgeBaseIndex.load_from_json(index_path)

    if args.format:
        docs = index.filter_by_format(args.format)
    else:
        docs = index.list_documents()

    print(f"Listing {len(docs)} indexed document(s):\n")
    header = f"{'ID':<14} {'FORMAT':<8} {'WORDS':<8} {'DATE':<12} {'TITLE'}"
    print(header)
    print("-" * len(header))
    for doc in docs:
        d_str = doc.date or "-"
        print(f"{doc.doc_id:<14} {doc.format.upper():<8} {doc.word_count:<8} {d_str:<12} {doc.title}")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    """Display summary metrics and statistics for an index."""
    index_path = Path(args.index)
    if not index_path.exists():
        print(f"Error: Index file '{args.index}' does not exist.", file=sys.stderr)
        return 1

    index = KnowledgeBaseIndex.load_from_json(index_path)
    stats = index.get_statistics()

    print("=" * 50)
    print("KNOWLEDGE BASE ARCHIVE STATISTICS")
    print("=" * 50)
    print(f"Total Documents:     {stats['total_documents']}")
    print(f"Total Words:         {stats['total_words']:,}")
    print(f"Average Words/Doc:   {stats['average_words']}")
    dates = stats.get("dates", {})
    print(f"Date Range:          {dates.get('earliest') or 'N/A'} to {dates.get('latest') or 'N/A'}")

    print("\nBreakdown by Format:")
    for fmt, count in sorted(stats.get("formats", {}).items()):
        print(f" - {fmt.upper():<6} : {count} documents")

    print("\nTop Longest Documents:")
    for idx, item in enumerate(stats.get("longest_documents", []), start=1):
        print(f" {idx}. {item['title']} ({item['words']} words, {item['format'].upper()})")
    print("=" * 50)
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct CLI argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="kbparser",
        description="Knowledge Base Document Parser and Indexer",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: build
    p_build = subparsers.add_parser("build", help="Parse a folder and generate a JSON index")
    p_build.add_argument("directory", help="Path to documents folder")
    p_build.add_argument(
        "-o", "--output",
        default="knowledge_base.json",
        help="Target JSON index file (default: knowledge_base.json)",
    )
    p_build.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Scan subdirectories recursively",
    )
    p_build.set_defaults(func=cmd_build)

    # Subcommand: search
    p_search = subparsers.add_parser("search", help="Search the index by keyword")
    p_search.add_argument("index", help="Path to JSON index file")
    p_search.add_argument("-q", "--query", required=True, help="Search query string")
    p_search.add_argument("-f", "--format", help="Filter results by format (txt, md, csv)")
    p_search.add_argument("--preview", action="store_true", help="Display document preview")
    p_search.add_argument("--title-only", action="store_true", help="Search only within titles")
    p_search.add_argument("--content-only", action="store_true", help="Search only within content")
    p_search.add_argument("-c", "--case-sensitive", action="store_true", help="Case sensitive search")
    p_search.set_defaults(func=cmd_search)

    # Subcommand: list
    p_list = subparsers.add_parser("list", help="List all indexed documents")
    p_list.add_argument("index", help="Path to JSON index file")
    p_list.add_argument("-f", "--format", help="Filter by format (txt, md, csv)")
    p_list.set_defaults(func=cmd_list)

    # Subcommand: stats
    p_stats = subparsers.add_parser("stats", help="Show archive statistics")
    p_stats.add_argument("index", help="Path to JSON index file")
    p_stats.set_defaults(func=cmd_stats)

    return parser


def main(argv: Optional[list] = None) -> int:
    """Main CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
