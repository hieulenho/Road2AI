from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "tmp/vn53_analysis_20260824"


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    records = json.loads((BUILD / "submission.json").read_text(encoding="utf-8"))
    for record in records:
        qid = int(record["id"])
        if qid < 578:
            continue
        zeroes = []
        for evidence in record["evidence"]:
            with (BUILD / evidence["csv_path"]).open(encoding="utf-8-sig", newline="") as stream:
                for row in csv.DictReader(stream):
                    value = row.get("value")
                    raw = str(row.get("raw_value", "")).strip()
                    if (value not in (None, "") and float(value) == 0.0) or raw in {"-", "–", "—"}:
                        zeroes.append(
                            f"{row.get('doc_id')} T{row.get('table_id')} R{row.get('row_idx')}C{row.get('col_idx')} "
                            f"label={row.get('label') or row.get('row_label')} raw={raw}"
                        )
        if zeroes:
            print(f"Q{qid} answer={record['answer']}\n  {record['question']}")
            for item in zeroes:
                print(f"  {item}")


if __name__ == "__main__":
    main()
