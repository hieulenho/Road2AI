from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> tuple[zipfile.ZipFile, dict[int, dict]]:
    archive = zipfile.ZipFile(path)
    json_name = next(name for name in archive.namelist() if name.endswith(".json"))
    rows = json.loads(archive.read(json_name).decode("utf-8"))
    return archive, {int(row["id"]): row for row in rows}


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("qids")
    parser.add_argument("--base", default="submission_vn53.zip")
    parser.add_argument("--alternate", default="submission_vn4.zip")
    args = parser.parse_args()
    qids = [int(value) for value in args.qids.split(",")]
    base_zip, base = load(ROOT / args.base)
    alt_zip, alt = load(ROOT / args.alternate)
    try:
        for qid in qids:
            print(f"\n{'=' * 28} Q{qid} {'=' * 28}")
            for label, archive, rows in (("BASE", base_zip, base), ("ALT", alt_zip, alt)):
                row = rows[qid]
                print(f"[{label}] answer={row['answer']!r}")
                print(f"query={row['pandas_query']}")
                print(f"tables={row['relevant_tables']}")
                for evidence in row["evidence"]:
                    path = evidence["csv_path"]
                    print(f"--- {label} {evidence['variable']} {path} ---")
                    print(archive.read(path).decode("utf-8-sig").rstrip())
    finally:
        base_zip.close()
        alt_zip.close()


if __name__ == "__main__":
    main()
