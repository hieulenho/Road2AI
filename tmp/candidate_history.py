from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGETS = {611, 671, 685, 699, 700, 719, 882, 935, 979, 992, 1001, 1012}

history = json.loads((ROOT / "runs/live_search/submission_history.json").read_text(encoding="utf-8"))
scores: dict[int, float] = {}
for item in history:
    match = re.fullmatch(r"submission_vn(\d+)\.zip", str(item.get("filename", "")))
    if not match:
        continue
    score = next(
        (row.get("score") for row in item.get("scores", []) if row.get("column_key") == "EXECUTION_ACCURACY"),
        None,
    )
    if score is not None:
        scores[int(match.group(1))] = float(score)

previous: dict[int, float] = {}
for version in sorted(scores):
    path = ROOT / f"submission_vn{version}.zip"
    if not path.exists():
        continue
    with zipfile.ZipFile(path) as archive:
        name = next(name for name in archive.namelist() if name.lower().endswith(".json"))
        rows = json.loads(archive.read(name))
    current = {int(row["id"]): float(row["answer"]) for row in rows if int(row["id"]) in TARGETS}
    changes = {qid: value for qid, value in current.items() if previous.get(qid) != value}
    if changes:
        print(f"vn{version:02d} score={scores[version]:.4f} changes={changes}")
    previous = current
