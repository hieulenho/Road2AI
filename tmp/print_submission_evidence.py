from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QIDS = [183, 197, 248, 425, 658, 671, 787, 993]

with zipfile.ZipFile(ROOT / "submission_vn75.zip") as archive:
    rows = {int(row["id"]): row for row in json.loads(archive.read("submission.json"))}
    for qid in QIDS:
        print(f"Q{qid}")
        for evidence in rows[qid]["evidence"]:
            print(archive.read(evidence["csv_path"]).decode("utf-8"))
