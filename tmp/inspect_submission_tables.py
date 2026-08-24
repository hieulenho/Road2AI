from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import sys
from pathlib import Path

from road2ai_vifinqa.paths import INDEX_PATH


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "tmp/vn53_analysis_20260824"


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("ids", nargs="+", type=int)
    args = parser.parse_args()
    submission = {
        int(row["id"]): row
        for row in json.loads((BUILD / "submission.json").read_text(encoding="utf-8"))
    }
    connection = sqlite3.connect(f"file:{INDEX_PATH.as_posix()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    for qid in args.ids:
        record = submission[qid]
        print(f"\n===== Q{qid} answer={record['answer']}\n{record['question']}")
        seen: set[tuple[str, int]] = set()
        for evidence in record["evidence"]:
            with (BUILD / evidence["csv_path"]).open(encoding="utf-8-sig", newline="") as stream:
                selected = list(csv.DictReader(stream))
            for source in selected:
                if not source.get("doc_id") or not source.get("table_id"):
                    continue
                key = (source["doc_id"], int(source["table_id"]))
                print(
                    "SELECTED "
                    f"{source['doc_id']}|{source['table_id']} "
                    f"r{source.get('row_idx')}c{source.get('col_idx')} "
                    f"label={source.get('row_label') or source.get('label')} "
                    f"raw={source.get('raw_value')}"
                )
                if key in seen:
                    continue
                seen.add(key)
                context = connection.execute(
                    "SELECT context FROM tables WHERE doc_id=? AND table_id=?",
                    key,
                ).fetchone()
                print(f"CONTEXT {context['context'] if context else ''}")
                rows = connection.execute(
                    "SELECT row_idx,cells_json FROM rows WHERE doc_id=? AND table_id=? ORDER BY row_idx",
                    key,
                )
                for row in rows:
                    print(f"  r{row['row_idx']}: {json.loads(row['cells_json'])}")


if __name__ == "__main__":
    main()
