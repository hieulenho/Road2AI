from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
history = json.loads((ROOT / "runs/live_search/submission_history.json").read_text(encoding="utf-8"))
scores: dict[int, float] = {}
for item in history:
    match = re.fullmatch(r"submission_vn(\d+)\.zip", str(item.get("filename", "")))
    if not match:
        continue
    execution = next(
        (row for row in item.get("scores", []) if row.get("column_key") == "EXECUTION_ACCURACY"),
        None,
    )
    if execution:
        scores[int(match.group(1))] = float(execution["score"])


def load(version: int) -> dict[int, dict[str, object]]:
    path = ROOT / f"submission_vn{version}.zip"
    with zipfile.ZipFile(path) as archive:
        names = [name for name in archive.namelist() if name.lower().endswith(".json")]
        if len(names) != 1:
            raise RuntimeError(f"{path}: expected one JSON, got {names}")
        rows = json.loads(archive.read(names[0]))
    return {int(row["id"]): row for row in rows}


previous_version: int | None = None
previous_rows: dict[int, dict[str, object]] | None = None
for version in sorted(scores):
    path = ROOT / f"submission_vn{version}.zip"
    if not path.exists():
        continue
    rows = load(version)
    if previous_rows is not None and previous_version is not None:
        changed = [
            qid
            for qid in sorted(rows)
            if float(rows[qid]["answer"]) != float(previous_rows[qid]["answer"])
        ]
        delta = scores[version] - scores[previous_version]
        print(
            f"vn{previous_version:02d}->vn{version:02d} "
            f"score {scores[previous_version]:.4f}->{scores[version]:.4f} "
            f"delta={delta:+.4f} changed={len(changed)} ids={changed}"
        )
        if len(changed) <= 30:
            for qid in changed:
                print(
                    f"  Q{qid}: {previous_rows[qid]['answer']} -> {rows[qid]['answer']}"
                )
    previous_version = version
    previous_rows = rows
