from __future__ import annotations

import csv
import json
import random
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "tmp/vn53_analysis_20260824"


def main() -> None:
    connection = sqlite3.connect(ROOT / "artifacts/tables.sqlite3")
    pairs = [
        (str(doc_id), int(table_id))
        for doc_id, table_id in connection.execute(
            "SELECT doc_id,table_id FROM tables ORDER BY doc_id,table_id"
        )
    ]
    random.Random(42).shuffle(pairs)
    rank = {pair: index for index, pair in enumerate(pairs, 1)}
    records = json.loads((BUILD / "submission.json").read_text(encoding="utf-8"))
    for record in records[:30]:
        selected: list[tuple[str, int]] = []
        for evidence in record["evidence"]:
            with (BUILD / evidence["csv_path"]).open(encoding="utf-8-sig", newline="") as stream:
                for row in csv.DictReader(stream):
                    if row.get("doc_id") and row.get("table_id"):
                        selected.append((row["doc_id"], int(row["table_id"])))
        unique = list(dict.fromkeys(selected))
        print(
            f"Q{record['id']:03d} "
            + ", ".join(f"rank={rank.get(pair)} {pair[0]}|{pair[1]}" for pair in unique)
        )


if __name__ == "__main__":
    main()
