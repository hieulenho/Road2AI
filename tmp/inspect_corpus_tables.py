"""Print selected corpus tables for manual source verification."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from road2ai_vifinqa.corpus import Corpus  # noqa: E402


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 3:
        raise SystemExit("usage: inspect_corpus_tables.py DOC_ID TABLE_ID [TABLE_ID ...]")
    doc_id = sys.argv[1]
    table_ids = [int(value) for value in sys.argv[2:]]
    with Corpus() as corpus:
        for table_id in table_ids:
            table = corpus.table(doc_id, table_id)
            print(f"\n===== {doc_id}|table_{table_id} =====")
            print(table.context)
            for index, row in enumerate(table.rows):
                print(f"{index:03d}: {list(row)}")


if __name__ == "__main__":
    main()
